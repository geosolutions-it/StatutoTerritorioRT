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
import datetime
import graphene
import traceback

from django.conf import settings

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.api.graphene.mutations.piano import check_and_promote
from serapide_core.api.piano_utils import (
    needs_execution,
    is_executed,
    ensure_fase,
    chiudi_azione,
    crea_azione,
    chiudi_pendenti,
)
from serapide_core.helpers import update_create_instance

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    ProceduraApprovazione,
    ProceduraPubblicazione,

)

from serapide_core.modello.enums import (
    STATO_AZIONE,
    TipologiaAzione,
    QualificaRichiesta,
)

from serapide_core.api.graphene import (
    types, inputs)

import serapide_core.api.auth.user as auth
import serapide_core.api.auth.piano as auth_piano
from strt_users.enums import Qualifica

logger = logging.getLogger(__name__)


# class CreateProceduraApprovazione(relay.ClientIDMutation):
#
#     class Input:
#         procedura_approvazione = graphene.Argument(inputs.ProceduraApprovazioneCreateInput)
#         codice_piano = graphene.String(required=True)
#
#     nuova_procedura_approvazione = graphene.Field(types.ProceduraApprovazioneNode)
#
#     @classmethod
#     def mutate_and_get_payload(cls, root, info, **input):
#         _piano = Piano.objects.get(codice=input['codice_piano'])
#         _procedura_approvazione_data = input.get('procedura_approvazione')
#         if info.context.user and \
#         rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
#         rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
#             try:
#                 # ProceduraApprovazione (M)
#                 _procedura_approvazione_data['piano'] = _piano
#                 # Ente (M)
#                 _procedura_approvazione_data['ente'] = _piano.ente
#
#                 _procedura_approvazione = ProceduraApprovazione()
#                 _procedura_approvazione.piano = _piano
#                 _procedura_approvazione.ente = _piano.ente
#                 _procedura_approvazione_data['id'] = _procedura_approvazione.id
#                 _procedura_approvazione_data['uuid'] = _procedura_approvazione.uuid
#                 nuova_procedura_approvazione = update_create_instance(
#                     _procedura_approvazione, _procedura_approvazione_data)
#
#                 _piano.procedura_approvazione = nuova_procedura_approvazione
#                 _piano.save()
#
#                 return cls(nuova_procedura_approvazione=nuova_procedura_approvazione)
#             except BaseException as e:
#                 tb = traceback.format_exc()
#                 logger.error(tb)
#                 return GraphQLError(e, code=500)
#         else:
#             return GraphQLError(_("Forbidden"), code=403)


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
        _piano = _procedura_approvazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        for fixed_field in ['uuid', 'piano', 'data_creazione', 'ente']:
            if fixed_field in _procedura_approvazione_data:
                logger.warning('Il campo "{}" non può essere modificato'.format(fixed_field))
                _procedura_approvazione_data.pop(fixed_field)

        try:
            procedura_approvazione_aggiornata = update_create_instance(
                _procedura_approvazione, _procedura_approvazione_data)

            return cls(procedura_approvazione_aggiornata=procedura_approvazione_aggiornata)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class TrasmissioneApprovazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.trasmissione_approvazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_approvazione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ADOZIONE)

        _trasmissione_approvazione = piano.getFirstAction(TipologiaAzione.trasmissione_approvazione)
        if needs_execution(_trasmissione_approvazione):
            chiudi_azione(_trasmissione_approvazione)

            if not piano.procedura_adozione.richiesta_conferenza_paesaggistica:
                # Se non è stata fatta prima, va fatta ora...
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.esito_conferenza_paesaggistica_ap,
                        qualifica_richiesta=QualificaRichiesta.REGIONE,
                        stato=STATO_AZIONE.attesa
                    ))

                procedura_approvazione.richiesta_conferenza_paesaggistica = True
                procedura_approvazione.save()

            else:
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.pubblicazione_approvazione,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=STATO_AZIONE.necessaria
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

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


class EsitoConferenzaPaesaggisticaAP(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.esito_conferenza_paesaggistica_ap

    @staticmethod
    def procedura(piano):
        return piano.procedura_approvazione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ADOZIONE)

        _esito_cp = piano.getFirstAction(TipologiaAzione.esito_conferenza_paesaggistica_ap)

        if needs_execution(_esito_cp):
            chiudi_azione(_esito_cp)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.pubblicazione_approvazione,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.necessaria
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user)

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


class PubblicazioneApprovazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.pubblicazione_approvazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_approvazione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ADOZIONE)

        _pubblicazione_approvazione = piano.getFirstAction(TipologiaAzione.pubblicazione_approvazione)

        if needs_execution(_pubblicazione_approvazione):
            chiudi_azione(_pubblicazione_approvazione)

            _trasmissione_approvazione = piano.getFirstAction(TipologiaAzione.trasmissione_approvazione)
            _expire_days = getattr(settings, 'ATTRIBUZIONE_CONFORMITA_PIT_EXPIRE_DAYS', 30)
            _alert_delta = datetime.timedelta(days=_expire_days)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.attribuzione_conformita_pit,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=STATO_AZIONE.attesa,
                    data=_trasmissione_approvazione.data + _alert_delta
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="rev_piano_post_cp")

            return PubblicazioneApprovazione(
                approvazione_aggiornata=_procedura_approvazione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class AttribuzioneConformitaPIT(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.attribuzione_conformita_pit

    @staticmethod
    def procedura(piano):
        return piano.procedura_approvazione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_approvazione, user):

        ensure_fase(fase, Fase.ADOZIONE)

        _attribuzione_conformita_pit = piano.getFirstAction(TipologiaAzione.attribuzione_conformita_pit)

        if needs_execution(_attribuzione_conformita_pit):
            chiudi_azione(_attribuzione_conformita_pit)

        if not procedura_approvazione.conclusa:
            chiudi_pendenti(piano, attesa=True, necessaria=False)
            procedura_approvazione.conclusa = True
            procedura_approvazione.save()

            procedura_pubblicazione, created = ProceduraPubblicazione.objects.get_or_create(piano=piano)
            piano.procedura_pubblicazione = procedura_pubblicazione
            piano.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=input['uuid'])
        _piano = _procedura_approvazione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_approvazione, info.context.user)

            check_and_promote(_piano, info)

            return AttribuzioneConformitaPIT(
                approvazione_aggiornata=_procedura_approvazione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)
