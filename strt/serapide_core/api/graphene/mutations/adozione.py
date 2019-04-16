# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import rules
import logging
import datetime
import graphene
import traceback

from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.helpers import update_create_instance

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    AzioniPiano,
    ProceduraAdozione,
)

from serapide_core.modello.enums import (
    FASE,
    STATO_AZIONE,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
)

from . import fase
from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateProceduraAdozione(relay.ClientIDMutation):

    class Input:
        procedura_adozione = graphene.Argument(inputs.ProceduraAdozioneCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_adozione = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_adozione_data = input.get('procedura_adozione')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraAdozione (M)
                _procedura_adozione_data['piano'] = _piano
                # Ente (M)
                _procedura_adozione_data['ente'] = _piano.ente

                _procedura_adozione = ProceduraAdozione()
                _procedura_adozione.piano = _piano
                _procedura_adozione.ente = _piano.ente
                _procedura_adozione_data['id'] = _procedura_adozione.id
                _procedura_adozione_data['uuid'] = _procedura_adozione.uuid
                nuova_procedura_adozione = update_create_instance(_procedura_adozione, _procedura_adozione_data)

                _piano.procedura_adozione = nuova_procedura_adozione
                _piano.save()

                return cls(nuova_procedura_adozione=nuova_procedura_adozione)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraAdozione(relay.ClientIDMutation):

    class Input:
        procedura_adozione = graphene.Argument(inputs.ProceduraAdozioneUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _procedura_adozione_data = input.get('procedura_adozione')
        if 'piano' in _procedura_adozione_data:
            # This cannot be changed
            _procedura_adozione_data.pop('piano')
        _piano = _procedura_adozione.piano
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        # _ente = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_adozione_data:
                    _procedura_adozione_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_adozione_data:
                    _procedura_adozione_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_adozione_data:
                    _procedura_adozione_data.pop('ente')
                    # This cannot be changed

                procedura_adozione_aggiornata = update_create_instance(_procedura_adozione, _procedura_adozione_data)

                if procedura_adozione_aggiornata.data_delibera_adozione:
                    _expire_days = getattr(settings, 'ADOZIONE_RICEZIONE_PARERI_EXPIRE_DAYS', 30)
                    _alert_delta = datetime.timedelta(days=_expire_days)
                    procedura_adozione_aggiornata.data_ricezione_pareri = \
                        procedura_adozione_aggiornata.data_delibera_adozione + _alert_delta

                if procedura_adozione_aggiornata.pubblicazione_burt_data:
                    _expire_days = getattr(settings, 'ADOZIONE_RICEZIONE_OSSERVAZIONI_EXPIRE_DAYS', 30)
                    _alert_delta = datetime.timedelta(days=_expire_days)
                    procedura_adozione_aggiornata.data_ricezione_osservazioni = \
                        procedura_adozione_aggiornata.pubblicazione_burt_data + _alert_delta

                procedura_adozione_aggiornata.save()

                return cls(procedura_adozione_aggiornata=procedura_adozione_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class TrasmissioneAdozione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _trasmissione_adozione = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.trasmissione_adozione).first()
            if _trasmissione_adozione and _trasmissione_adozione.stato != STATO_AZIONE.nessuna:
                _trasmissione_adozione.stato = STATO_AZIONE.nessuna
                _trasmissione_adozione.data = datetime.datetime.now(timezone.get_current_timezone())
                _trasmissione_adozione.save()

                _osservazioni_enti = Azione(
                    tipologia=TIPOLOGIA_AZIONE.osservazioni_enti,
                    attore=TIPOLOGIA_ATTORE.enti,
                    order=_order,
                    stato=STATO_AZIONE.attesa,
                    data=procedura_adozione.data_ricezione_osservazioni
                )
                _osservazioni_enti.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_osservazioni_enti, piano=piano)

                _osservazioni_regione = Azione(
                    tipologia=TIPOLOGIA_AZIONE.osservazioni_regione,
                    attore=TIPOLOGIA_ATTORE.regione,
                    order=_order,
                    stato=STATO_AZIONE.attesa,
                    data=procedura_adozione.data_ricezione_osservazioni
                )
                _osservazioni_regione.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_osservazioni_regione, piano=piano)

                _upload_osservazioni_privati = Azione(
                    tipologia=TIPOLOGIA_AZIONE.upload_osservazioni_privati,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.attesa,
                    data=procedura_adozione.data_ricezione_osservazioni
                )
                _upload_osservazioni_privati.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_upload_osservazioni_privati, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="trasmissione_adozione")

                return TrasmissioneAdozione(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class TrasmissioneOsservazioni(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _osservazioni_enti = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.osservazioni_enti).first()

            _osservazioni_regione = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.osservazioni_regione).first()

            _upload_osservazioni_privati = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.upload_osservazioni_privati).first()

            _organization = piano.ente

            if rules.test_rule('strt_core.api.is_actor', token or (user, _organization), 'Regione'):
                if _osservazioni_regione and _osservazioni_regione.stato != STATO_AZIONE.nessuna:
                    _osservazioni_regione.stato = STATO_AZIONE.nessuna
                    _osservazioni_regione.data = datetime.datetime.now(timezone.get_current_timezone())
                    _osservazioni_regione.save()

                    if _osservazioni_enti and _osservazioni_enti.stato != STATO_AZIONE.nessuna:
                        _osservazioni_enti.stato = STATO_AZIONE.nessuna
                        _osservazioni_enti.data = datetime.datetime.now(timezone.get_current_timezone())
                        _osservazioni_enti.save()

            if rules.test_rule('strt_core.api.is_actor', token or (user, _organization), 'Comune'):
                if _upload_osservazioni_privati and _upload_osservazioni_privati.stato != STATO_AZIONE.nessuna:
                    _upload_osservazioni_privati.stato = STATO_AZIONE.nessuna
                    _upload_osservazioni_privati.data = datetime.datetime.now(timezone.get_current_timezone())
                    _upload_osservazioni_privati.save()

            if _upload_osservazioni_privati.stato == STATO_AZIONE.nessuna and \
            _osservazioni_regione.stato == STATO_AZIONE.nessuna:
                _controdeduzioni = Azione(
                    tipologia=TIPOLOGIA_AZIONE.controdeduzioni,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.attesa
                )
                _controdeduzioni.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_controdeduzioni, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user, _token)

                return TrasmissioneOsservazioni(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class Controdeduzioni(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _controdeduzioni = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.controdeduzioni).first()

            if _controdeduzioni and _controdeduzioni.stato != STATO_AZIONE.nessuna:
                _controdeduzioni.stato = STATO_AZIONE.nessuna
                _controdeduzioni.data = datetime.datetime.now(timezone.get_current_timezone())
                _controdeduzioni.save()

                _piano_controdedotto = Azione(
                    tipologia=TIPOLOGIA_AZIONE.piano_controdedotto,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.attesa
                )
                _piano_controdedotto.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_piano_controdedotto, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user, _token)

                return Controdeduzioni(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class PianoControdedotto(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _piano_controdedotto = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.piano_controdedotto).first()

            if _piano_controdedotto and _piano_controdedotto.stato != STATO_AZIONE.nessuna and \
            procedura_adozione.url_piano_controdedotto:
                _piano_controdedotto.stato = STATO_AZIONE.nessuna
                _piano_controdedotto.data = datetime.datetime.now(timezone.get_current_timezone())
                _piano_controdedotto.save()

                if not procedura_adozione.richiesta_conferenza_paesaggistica:

                    piano.chiudi_pendenti()

                    procedura_adozione.conclusa = True
                    procedura_adozione.save()
                else:
                    _convocazione_cp = Azione(
                        tipologia=TIPOLOGIA_AZIONE.esito_conferenza_paesaggistica,
                        attore=TIPOLOGIA_ATTORE.regione,
                        order=_order,
                        stato=STATO_AZIONE.attesa
                    )
                    _convocazione_cp.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_convocazione_cp, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user, _token)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="piano_controdedotto")

                if _piano.is_eligible_for_promotion:
                    _piano.fase = _fase = Fase.objects.get(nome=_piano.next_phase)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    _piano.save()
                    fase.promuovi_piano(_fase, _piano)

                return PianoControdedotto(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class EsitoConferenzaPaesaggistica(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _esito_cp = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.esito_conferenza_paesaggistica).first()

            if _esito_cp and _esito_cp.stato != STATO_AZIONE.nessuna:
                _esito_cp.stato = STATO_AZIONE.nessuna
                _esito_cp.data = datetime.datetime.now(timezone.get_current_timezone())
                _esito_cp.save()

                _rev_piano_post_cp = Azione(
                    tipologia=TIPOLOGIA_AZIONE.rev_piano_post_cp,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.necessaria
                )
                _rev_piano_post_cp.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_rev_piano_post_cp, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Regione'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user, _token)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="esito_conferenza_paesaggistica")

                return EsitoConferenzaPaesaggistica(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class RevisionePianoPostConfPaesaggistica(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user, token):

        # Update Azioni Piano
        # - Update Action state accordingly
        if fase.nome == FASE.avvio:
            _rev_piano_post_cp = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.rev_piano_post_cp).first()

            if _rev_piano_post_cp and _rev_piano_post_cp.stato != STATO_AZIONE.nessuna and \
            procedura_adozione.url_rev_piano_post_cp:
                _rev_piano_post_cp.stato = STATO_AZIONE.nessuna
                _rev_piano_post_cp.data = datetime.datetime.now(timezone.get_current_timezone())
                _rev_piano_post_cp.save()

                piano.chiudi_pendenti()

                procedura_adozione.conclusa = True
                procedura_adozione.save()
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user, _token)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="rev_piano_post_cp")

                if _piano.is_eligible_for_promotion:
                    _piano.fase = _fase = Fase.objects.get(nome=_piano.next_phase)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    _piano.save()
                    fase.promuovi_piano(_fase, _piano)

                return RevisionePianoPostConfPaesaggistica(
                    adozione_aggiornata=_procedura_adozione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
