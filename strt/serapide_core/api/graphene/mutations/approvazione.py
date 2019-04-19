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
    ProceduraApprovazione,
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


class CreateProceduraApprovazione(relay.ClientIDMutation):

    class Input:
        procedura_approvazione = graphene.Argument(inputs.ProceduraApprovazioneCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_approvazione = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_approvazione_data = input.get('procedura_approvazione')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraApprovazione (M)
                _procedura_approvazione_data['piano'] = _piano
                # Ente (M)
                _procedura_approvazione_data['ente'] = _piano.ente

                _procedura_approvazione = ProceduraApprovazione()
                _procedura_approvazione.piano = _piano
                _procedura_approvazione.ente = _piano.ente
                _procedura_approvazione_data['id'] = _procedura_approvazione.id
                _procedura_approvazione_data['uuid'] = _procedura_approvazione.uuid
                nuova_procedura_approvazione = update_create_instance(
                    _procedura_approvazione, _procedura_approvazione_data)

                _piano.procedura_approvazione = nuova_procedura_approvazione
                _piano.save()

                return cls(nuova_procedura_approvazione=nuova_procedura_approvazione)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraApprovazione(relay.ClientIDMutation):

    class Input:
        procedura_approvazione = graphene.Argument(inputs.ProceduraApprovazioneUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _procedura_approvazione_data = input.get('procedura_approvazione')
        if 'piano' in _procedura_approvazione_data:
            # This cannot be changed
            _procedura_approvazione_data.pop('piano')
        _piano = _procedura_approvazione.piano
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        # _ente = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_approvazione_data:
                    _procedura_approvazione_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_approvazione_data:
                    _procedura_approvazione_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_approvazione_data:
                    _procedura_approvazione_data.pop('ente')
                    # This cannot be changed

                procedura_approvazione_aggiornata = update_create_instance(
                    _procedura_approvazione, _procedura_approvazione_data)
                return cls(procedura_approvazione_aggiornata=procedura_approvazione_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class TrasmissioneApprovazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.adozione:
            _trasmissione_approvazione = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.trasmissione_approvazione).first()
            if _trasmissione_approvazione and _trasmissione_approvazione.stato != STATO_AZIONE.nessuna:
                _trasmissione_approvazione.stato = STATO_AZIONE.nessuna
                _trasmissione_approvazione.data = datetime.datetime.now(timezone.get_current_timezone())
                _trasmissione_approvazione.save()

                _expire_days = getattr(settings, 'ATTRIBUZIONE_CONFORMITA_PIT_EXPIRE_DAYS', 30)
                _alert_delta = datetime.timedelta(days=_expire_days)
                _attribuzione_conformita_pit = Azione(
                    tipologia=TIPOLOGIA_AZIONE.attribuzione_conformita_pit,
                    attore=TIPOLOGIA_ATTORE.regione,
                    order=_order,
                    stato=STATO_AZIONE.attesa,
                    data=_trasmissione_approvazione.data + _alert_delta
                )
                _attribuzione_conformita_pit.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_attribuzione_conformita_pit, piano=piano)

                if not piano.procedura_adozione.richiesta_conferenza_paesaggistica:
                    # Se non è stata fatta prima, va fatta ora...
                    procedura_approvazione.richiesta_conferenza_paesaggistica = True
                    procedura_approvazione.save()

                    _convocazione_cp = Azione(
                        tipologia=TIPOLOGIA_AZIONE.esito_conferenza_paesaggistica_ap,
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
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="trasmissione_approvazione")

                return TrasmissioneApprovazione(
                    approvazione_aggiornata=_procedura_approvazione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class EsitoConferenzaPaesaggisticaAP(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.adozione:
            _esito_cp = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.esito_conferenza_paesaggistica_ap).first()

            if _esito_cp and _esito_cp.stato != STATO_AZIONE.nessuna:
                _esito_cp.stato = STATO_AZIONE.nessuna
                _esito_cp.data = datetime.datetime.now(timezone.get_current_timezone())
                _esito_cp.save()

                _rev_piano_post_cp = Azione(
                    tipologia=TIPOLOGIA_AZIONE.rev_piano_post_cp_ap,
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
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Regione'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user, _token)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="esito_conferenza_paesaggistica")

                return EsitoConferenzaPaesaggisticaAP(
                    approvazione_aggiornata=_procedura_approvazione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class RevisionePianoPostConfPaesaggisticaAP(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user, token):

        # Update Azioni Piano
        # - Update Action state accordingly
        if fase.nome == FASE.adozione:
            _rev_piano_post_cp = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.rev_piano_post_cp_ap).first()

            if _rev_piano_post_cp and _rev_piano_post_cp.stato != STATO_AZIONE.nessuna:
                _rev_piano_post_cp.stato = STATO_AZIONE.nessuna
                _rev_piano_post_cp.data = datetime.datetime.now(timezone.get_current_timezone())
                _rev_piano_post_cp.save()

                piano.chiudi_pendenti()
                procedura_approvazione.conclusa = True
                procedura_approvazione.save()

                # TODO: Procedura Pubblicazione
                # procedura_approvazione, created = ProceduraApprovazione.objects.get_or_create(
                #     piano=piano, ente=piano.ente)
                # piano.procedura_approvazione = procedura_approvazione
                # piano.save()
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user, _token)

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

                return RevisionePianoPostConfPaesaggisticaAP(
                    approvazione_aggiornata=_procedura_approvazione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
