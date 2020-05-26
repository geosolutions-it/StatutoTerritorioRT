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

import logging
import graphene
import traceback

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.helpers import update_create_instance

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Piano,
    ProceduraPubblicazione,
)

from serapide_core.api.piano_utils import (
    needs_execution,
    is_executed,
    ensure_fase,
    chiudi_azione,
    crea_azione,
    chiudi_pendenti,
)

from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TipologiaAzione,
)

import serapide_core.api.auth.user as auth
from serapide_core.api.graphene import (types, inputs)
from strt_users.enums import Qualifica

logger = logging.getLogger(__name__)


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

        _piano = _procedura_pubblicazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        for fixed_field in ['uuid', 'piano', 'data_creazione', 'ente']:
            if fixed_field in _procedura_pubblicazione_data:
                logger.warning('Il campo "{}" non può essere modificato'.format(fixed_field))
                _procedura_pubblicazione_data.pop(fixed_field)

        try:
            procedura_pubblicazione_aggiornata = update_create_instance(
                _procedura_pubblicazione, _procedura_pubblicazione_data)
            return cls(procedura_pubblicazione_aggiornata=procedura_pubblicazione_aggiornata)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class PubblicazionePiano(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    pubblicazione_aggiornata = graphene.Field(types.ProceduraPubblicazioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.pubblicazione_piano

    @staticmethod
    def procedura(piano):
        return piano.procedura_pubblicazione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_pubblicazione, user):

        ensure_fase(fase, Fase.APPROVAZIONE)

        # - Update Action state accordingly
        _pubblicazione_piano = piano.getFirstAction(TipologiaAzione.pubblicazione_piano)

        if needs_execution(_pubblicazione_piano):
            chiudi_azione(_pubblicazione_piano)

        if not procedura_pubblicazione.conclusa:
            chiudi_pendenti(piano, attesa=True, necessaria=True)
            procedura_pubblicazione.data_pubblicazione = _pubblicazione_piano.data
            procedura_pubblicazione.conclusa = True
            procedura_pubblicazione.save()
            piano.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_pubblicazione = ProceduraPubblicazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_pubblicazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_pubblicazione, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="pubblicazione_piano")

            return PubblicazionePiano(
                pubblicazione_aggiornata=_procedura_pubblicazione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)
