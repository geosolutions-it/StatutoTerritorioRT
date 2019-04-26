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
import graphene
import traceback

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
    ProceduraPubblicazione,
)

from serapide_core.modello.enums import (
    FASE,
    STATO_AZIONE,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
)

from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateProceduraPubblicazione(relay.ClientIDMutation):

    class Input:
        procedura_pubblicazione = graphene.Argument(inputs.ProceduraPubblicazioneCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_pubblicazione = graphene.Field(types.ProceduraPubblicazioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_pubblicazione_data = input.get('procedura_pubblicazione')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraPubblicazione (M)
                _procedura_pubblicazione_data['piano'] = _piano
                # Ente (M)
                _procedura_pubblicazione_data['ente'] = _piano.ente

                _procedura_pubblicazione = ProceduraPubblicazione()
                _procedura_pubblicazione.piano = _piano
                _procedura_pubblicazione.ente = _piano.ente
                _procedura_pubblicazione_data['id'] = _procedura_pubblicazione.id
                _procedura_pubblicazione_data['uuid'] = _procedura_pubblicazione.uuid
                nuova_procedura_pubblicazione = update_create_instance(
                    _procedura_pubblicazione, _procedura_pubblicazione_data)

                _piano.procedura_pubblicazione = nuova_procedura_pubblicazione
                _piano.save()

                return cls(nuova_procedura_pubblicazione=nuova_procedura_pubblicazione)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraPubblicazione(relay.ClientIDMutation):

    class Input:
        procedura_pubblicazione = graphene.Argument(inputs.ProceduraPubblicazioneUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_pubblicazione_aggiornata = graphene.Field(types.ProceduraPubblicazioneNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_pubblicazione = ProceduraPubblicazione.objects.get(uuid=input['uuid'])
        _procedura_pubblicazione_data = input.get('procedura_pubblicazione')
        if 'piano' in _procedura_pubblicazione_data:
            # This cannot be changed
            _procedura_pubblicazione_data.pop('piano')
        _piano = _procedura_pubblicazione.piano
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        # _ente = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_pubblicazione_data:
                    _procedura_pubblicazione_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_pubblicazione_data:
                    _procedura_pubblicazione_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_pubblicazione_data:
                    _procedura_pubblicazione_data.pop('ente')
                    # This cannot be changed

                procedura_pubblicazione_aggiornata = update_create_instance(
                    _procedura_pubblicazione, _procedura_pubblicazione_data)
                return cls(procedura_pubblicazione_aggiornata=procedura_pubblicazione_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class PubblicazionePiano(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    pubblicazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_pubblicazione, user, token):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        if fase.nome == FASE.adozione:
            _trasmissione_pubblicazione = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.trasmissione_pubblicazione).first()

            _pubblicazione_pubblicazione = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.pubblicazione_pubblicazione).first()

            if _pubblicazione_pubblicazione and _pubblicazione_pubblicazione.stato != STATO_AZIONE.nessuna:
                _pubblicazione_pubblicazione.stato = STATO_AZIONE.nessuna
                _pubblicazione_pubblicazione.data = datetime.datetime.now(timezone.get_current_timezone())
                _pubblicazione_pubblicazione.save()

                _expire_days = getattr(settings, 'ATTRIBUZIONE_CONFORMITA_PIT_EXPIRE_DAYS', 30)
                _alert_delta = datetime.timedelta(days=_expire_days)
                _attribuzione_conformita_pit = Azione(
                    tipologia=TIPOLOGIA_AZIONE.attribuzione_conformita_pit,
                    attore=TIPOLOGIA_ATTORE.regione,
                    order=_order,
                    stato=STATO_AZIONE.attesa,
                    data=_trasmissione_pubblicazione.data + _alert_delta
                )
                _attribuzione_conformita_pit.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_attribuzione_conformita_pit, piano=piano)
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_pubblicazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_pubblicazione.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_pubblicazione, info.context.user, _token)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="rev_piano_post_cp")

                return PubblicazionePiano(
                    pubblicazione_aggiornata=_procedura_pubblicazione,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
