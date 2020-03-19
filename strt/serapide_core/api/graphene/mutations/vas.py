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
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.api.graphene.mutations.piano import check_and_promote, try_and_close_avvio

from serapide_core.helpers import (
    is_RUP,
    update_create_instance)

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    ParereVAS,
    ProceduraVAS,
    ProceduraAvvio,
    ConsultazioneVAS,
    ParereVerificaVAS,
    SoggettoOperante,

    isExecuted,
    needsExecution,
    ensure_fase,
    crea_azione,
    chiudi_azione,
)
from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TipologiaVAS,
    TIPOLOGIA_AZIONE,
    # TIPOLOGIA_ATTORE,
)

from strt_users.enums import QualificaRichiesta, Qualifica


from serapide_core.api.graphene import (types, inputs)

import serapide_core.api.auth.user as auth
from strt_users.models import (
    Assegnatario,
)

logger = logging.getLogger(__name__)


def init_vas_procedure(piano:Piano):

    procedura_vas = piano.procedura_vas
    _verifica_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_verifica_vas)

    if _verifica_vas:
        if procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
            _verifica_vas.stato = STATO_AZIONE.nessuna

        elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO:

            _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
            chiudi_azione(_verifica_vas, datetime.datetime.now(timezone.get_current_timezone()) + \
                                 datetime.timedelta(days=_verifica_vas_expire_days))

            _avvio_consultazioni_sca_ac_expire_days = 10
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=STATO_AZIONE.attesa,
                    data=datetime.datetime.now(timezone.get_current_timezone()) +
                         datetime.timedelta(days=_avvio_consultazioni_sca_ac_expire_days)
                ))

        elif procedura_vas.tipologia == TipologiaVAS.SEMPLIFICATA:
            _verifica_vas.stato = STATO_AZIONE.nessuna

            _emissione_provvedimento_verifica_expire_days = 30
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.emissione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=STATO_AZIONE.attesa,
                    data=datetime.datetime.now(timezone.get_current_timezone()) +
                         datetime.timedelta(days=_emissione_provvedimento_verifica_expire_days)
                ))

        elif procedura_vas.tipologia in [TipologiaVAS.VERIFICA,
                                         TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO]:
            # _verifica_vas.stato = STATO_AZIONE.attesa
            _verifica_vas.stato = STATO_AZIONE.nessuna
            _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
            _verifica_vas.data = datetime.datetime.now(timezone.get_current_timezone()) + \
                                 datetime.timedelta(days=_verifica_vas_expire_days)

            _pareri_vas_expire_days = getattr(settings, 'PARERI_VERIFICA_VAS_EXPIRE_DAYS', 30)
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.pareri_verifica_vas,
                    qualifica_richiesta=QualificaRichiesta.SCA,
                    stato=STATO_AZIONE.attesa,
                    data=datetime.datetime.now(timezone.get_current_timezone()) +
                         datetime.timedelta(days=_pareri_vas_expire_days)
                ))

            _emissione_provvedimento_verifica_expire_days = 90
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.emissione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=STATO_AZIONE.attesa,
                    data=datetime.datetime.now(timezone.get_current_timezone()) +
                         datetime.timedelta(days=_emissione_provvedimento_verifica_expire_days)
                ))

        _verifica_vas.save()

# TODO: controllare se è davvero usata
# class CreateProceduraVAS(relay.ClientIDMutation):
#
#     class Input:
#         procedura_vas = graphene.Argument(inputs.ProceduraVASCreateInput)
#         codice_piano = graphene.String(required=True)
#
#     nuova_procedura_vas = graphene.Field(types.ProceduraVASNode)
#
#     @classmethod
#     def mutate_and_get_payload(cls, root, info, **input):
#         _piano = Piano.objects.get(codice=input['codice_piano'])
#         _procedura_vas_data = input.get('procedura_vas')
#         _role = info.context.session['role'] if 'role' in info.context.session else None
#         _token = info.context.session['token'] if 'token' in info.context.session else None
#         _ente = _piano.ente
#         if info.context.user and \
#         rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
#         rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
#         (rules.test_rule('strt_users.is_superuser', info.context.user) or
#          is_RUP(info.context.user) or
#          rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _ente), 'Comune')):
#             try:
#                 # ProceduraVAS (M)
#                 _procedura_vas_data['piano'] = _piano
#                 # Ente (M)
#                 _procedura_vas_data['ente'] = _piano.ente
#                 # Note (O)
#                 if 'note' in _procedura_vas_data:
#                     _data = _procedura_vas_data.pop('note')
#                     _procedura_vas_data['note'] = _data[0]
#
#                 _procedura_vas, created = ProceduraVAS.objects.get_or_create(
#                     piano=_piano,
#                     ente=_piano.ente)
#
#                 _procedura_vas_data['id'] = _procedura_vas.id
#                 _procedura_vas_data['uuid'] = _procedura_vas.uuid
#                 nuova_procedura_vas = update_create_instance(_procedura_vas, _procedura_vas_data)
#
#                 _piano.procedura_vas = nuova_procedura_vas
#                 _piano.save()
#
#                 return cls(nuova_procedura_vas=nuova_procedura_vas)
#             except BaseException as e:
#                 tb = traceback.format_exc()
#                 logger.error(tb)
#                 return GraphQLError(e, code=500)
#         else:
#             return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraVAS(relay.ClientIDMutation):

    class Input:
        procedura_vas = graphene.Argument(inputs.ProceduraVASUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _procedura_vas_data = input.get('procedura_vas')
        _piano = _procedura_vas.piano

        # _role = info.context.session['role'] if 'role' in info.context.session else None
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        _ente = _piano.ente

        if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
            if not auth.is_soggetto(info.context.user, _piano):
                return GraphQLError(_("Forbidden"), code=403)

        try:
            # These fields cannot be changed
            for field in ['piano', 'uuid', 'data_creazione', 'ente']:
                if 'field' in _procedura_vas_data:
                    logger.warning('Il campo "{}" non può essere modificato attraverso questa operazione'.format(field))
                    _procedura_vas_data.pop(field)

            # These fields can be changed by the RESP only
            # Tipologia (O)
            if 'tipologia' in _procedura_vas_data:
                _tipologia = _procedura_vas_data.pop('tipologia')
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
                    if _tipologia: #  and _tipologia in TipologiaVAS:
                        _tipo_parsed = TipologiaVAS.fix_enum(_tipologia, none_on_error=True)
                        if not _tipo_parsed:
                            return GraphQLError("Tipologia non riconosciuta [{}]".format(_tipologia), code=400)
                        _procedura_vas_data['tipologia'] = _tipo_parsed
                else:
                    logger.info('Non si hanno i privilegi per modificare il campo "tipologia"')

            # Note (O)
            if 'note' in _procedura_vas_data:
                _data = _procedura_vas_data.pop('note')
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
                    _procedura_vas.note = _data[0]
                else:
                    logger.info('Non si hanno i privilegi per modificare il campo "note"')

            # perform check before update
            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ap:
                if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
                    return GraphQLError("Forbidden - Non è permesso modificare un campo AP", code=403)

            # perform check before update
            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ac:
                if not auth.is_soggetto_operante(info.context.user, _piano, Qualifica.AC):
                    if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
                        return GraphQLError("Forbidden - Non è permesso modificare un campo AC", code=403)

            # update!
            procedura_vas_aggiornata = update_create_instance(_procedura_vas, _procedura_vas_data)

            # CHIUSURA AZIONI VAS
            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ap:
                _pubblicazione_provvedimento_verifica_ap = _piano.getFirstAction(
                        TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                        QualificaRichiesta.COMUNE)

                if needsExecution(_pubblicazione_provvedimento_verifica_ap):
                    chiudi_azione(_pubblicazione_provvedimento_verifica_ap, set_data=False)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_verifica_vas_updated")

            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ac:
                _pubblicazione_provvedimento_verifica_ac = _piano.getFirstAction(
                        TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                        qualifica_richiesta=QualificaRichiesta.AC)

                if needsExecution(_pubblicazione_provvedimento_verifica_ac):
                    chiudi_azione(_pubblicazione_provvedimento_verifica_ac, set_data=False)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_verifica_vas_updated")


            if isExecuted(_piano.getFirstAction(
                        TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                        qualifica_richiesta=QualificaRichiesta.AC)) and \
                isExecuted(_piano.getFirstAction(
                    TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.COMUNE)):

                procedura_vas_aggiornata.conclusa = True
                procedura_vas_aggiornata.save()

                if try_and_close_avvio(_piano):
                    check_and_promote(_piano, info)

            return cls(procedura_vas_aggiornata=procedura_vas_aggiornata)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class InvioPareriVerificaVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.pareri_verifica_vas

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _pareri_verifica_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_verifica_vas)
        if needsExecution(_pareri_verifica_vas):
            chiudi_azione(_pareri_verifica_vas)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        # _role = info.context.session['role'] if 'role' in info.context.session else None
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        # _organization = _piano.ente


        if not auth.is_soggetto_operante(info.context.user, _piano, Qualifica.SCA):
            return GraphQLError("Forbidden - Azione non permessa", code=403)

        # if info.context.user and \
        # rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        # rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'SCA'):
        try:
            _pareri_vas_count = ParereVerificaVAS.objects.filter(
                user=info.context.user,
                procedura_vas=_procedura_vas
            ).count()

            if _pareri_vas_count == 0:
                _parere_vas = ParereVerificaVAS(
                    inviata=True,
                    user=info.context.user,
                    procedura_vas=_procedura_vas
                )
                _parere_vas.save()
            elif _pareri_vas_count == 1:
                pass
            else:
                return GraphQLError("L'utente ha già inviato un parere verifica VAS", code=400)

            _tutti_pareri_inviati = True
            for _sca in SoggettoOperante.get_by_qualifica(_piano, Qualifica.SCA):

                # controlliamo che per ogni ufficio SCA assegnato come SO, almeno un assegnatario abbia inviato parere
                # TODO: controllare anche i token
                assegnatari = Assegnatario.objects.filter(qualifica_ufficio=_sca.qualifica_ufficio)
                users = [a.utente for a in assegnatari]
                _pareri_vas_exists = ParereVerificaVAS.objects.filter(
                    procedura_vas=_procedura_vas,
                    user__in=users,
                ).exists()
                if not _pareri_vas_exists:
                    _tutti_pareri_inviati = False
                    break

            if _tutti_pareri_inviati:

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="tutti_pareri_inviati")

                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return InvioPareriVerificaVAS(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class AssoggettamentoVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas):
        # Update Azioni Piano
        # - Complete Current Actions

        ensure_fase(fase, Fase.ANAGRAFICA)

        # - Update Action state accordingly
        if procedura_vas.assoggettamento:
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.avvio_esame_pareri_sca,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.necessaria
                ))

            procedura_vas.data_assoggettamento = datetime.datetime.now(timezone.get_current_timezone())
        else:
            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.necessaria
                ))

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=STATO_AZIONE.necessaria
                ))

            procedura_vas.non_necessaria = True

        procedura_vas.verifica_effettuata = True
        procedura_vas.save()

        _emissione_provvedimento_verifica = piano.getFirstAction(TIPOLOGIA_AZIONE.emissione_provvedimento_verifica)
        if needsExecution(_emissione_provvedimento_verifica):
            chiudi_azione(_emissione_provvedimento_verifica)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        # _role = info.context.session['role'] if 'role' in info.context.session else None
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        # _organization = _piano.ente

        if not auth.is_soggetto_operante(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Azione non permessa", code=403)
        # if info.context.user and \
        #         rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        #         rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC'):
        try:
            _pareri_verifica_vas = _piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_verifica_vas)

            if needsExecution(_pareri_verifica_vas) or \
                    _procedura_vas.verifica_effettuata or \
                    _procedura_vas.tipologia not in (TipologiaVAS.VERIFICA,
                                                     TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO,
                                                     TipologiaVAS.SEMPLIFICATA):
                return GraphQLError("Stato o tipo VAS errato", code=409)

            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas)

            return AssoggettamentoVAS(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class CreateConsultazioneVAS(relay.ClientIDMutation):

    class Input:
        codice_piano = graphene.String(required=True)

    nuova_consultazione_vas = graphene.Field(types.ConsultazioneVASNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas = ProceduraVAS.objects.get(piano=_piano)
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        (rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune') or
         rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC')):
            try:
                nuova_consultazione_vas = ConsultazioneVAS()
                nuova_consultazione_vas.user = info.context.user
                nuova_consultazione_vas.procedura_vas = _procedura_vas
                _consultazioni_vas_expire_days = getattr(settings, 'CONSULTAZIONI_SCA_EXPIRE_DAYS', 90)
                nuova_consultazione_vas.data_scadenza = datetime.datetime.now(timezone.get_current_timezone()) + \
                datetime.timedelta(days=_consultazioni_vas_expire_days)
                nuova_consultazione_vas.save()
                return cls(nuova_consultazione_vas=nuova_consultazione_vas)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateConsultazioneVAS(relay.ClientIDMutation):

    class Input:
        consultazione_vas = graphene.Argument(inputs.ConsultazioneVASUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    consultazione_vas_aggiornata = graphene.Field(types.ConsultazioneVASNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _consultazione_vas = ConsultazioneVAS.objects.get(uuid=input['uuid'])
        _consultazione_vas_data = input.get('consultazione_vas')
        _piano = _consultazione_vas.procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        (rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune') or
         rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC')):
            try:
                consultazione_vas_aggiornata = update_create_instance(_consultazione_vas, _consultazione_vas_data)
                return cls(consultazione_vas_aggiornata=consultazione_vas_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class AvvioConsultazioniVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    consultazione_vas_aggiornata = graphene.Field(types.ConsultazioneVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, consultazione_vas, user):

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_consultazioni_sca_list = Piano.azioni(tipologia_azione=TIPOLOGIA_AZIONE.avvio_consultazioni_sca)
        _avvio_consultazioni_sca = next((x for x in _avvio_consultazioni_sca_list if needsExecution(x)), None)

        if _avvio_consultazioni_sca:

            now = datetime.datetime.now(timezone.get_current_timezone())
            chiudi_azione(_avvio_consultazioni_sca, data=now)
            consultazione_vas.data_avvio_consultazioni_sca = now

            _pareri_vas_expire_days = getattr(settings, 'PARERI_VAS_EXPIRE_DAYS', 60)
            crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TIPOLOGIA_AZIONE.pareri_sca,
                        qualifica_richiesta=QualificaRichiesta.SCA,
                        stato=STATO_AZIONE.attesa,
                        data=datetime.datetime.now(timezone.get_current_timezone()) + datetime.timedelta(days=_pareri_vas_expire_days)
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _consultazione_vas = ConsultazioneVAS.objects.get(uuid=input['uuid'])
        _procedura_vas = _consultazione_vas.procedura_vas
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        (rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune') or
         rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC')):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _consultazione_vas, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="piano_verifica_vas_updated")

                return AvvioConsultazioniVAS(
                    consultazione_vas_aggiornata=_consultazione_vas,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class InvioPareriVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.avvio_consultazioni_sca

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _verifica_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_verifica_vas)

        _avvio_consultazioni_sca_list = Piano.azioni(tipologia_azione=TIPOLOGIA_AZIONE.avvio_consultazioni_sca)
        _avvio_consultazioni_sca = next((x for x in _avvio_consultazioni_sca_list if needsExecution(x)), None)

        _pareri_sca_list = Piano.azioni(tipologia_azione=TIPOLOGIA_AZIONE.pareri_sca)
        _pareri_sca = next((x for x in _pareri_sca_list if needsExecution(x)), None)

        if _verifica_vas:

            if not _pareri_sca:
                _pareri_sca = _pareri_sca_list.last()   # PERCHé?!?

            chiudi_azione(_pareri_sca)

            # TODO blocco if da rivedere
            if  (_avvio_consultazioni_sca or
                  ((_avvio_consultazioni_sca_list.count() == 1 and
                        procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO) or
                   (_avvio_consultazioni_sca_list.count() == 1 and
                        _avvio_consultazioni_sca_list.first().qualifica_richiesta == QualificaRichiesta.AC and
                        procedura_vas.tipologia != TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO))):

                if not _avvio_consultazioni_sca:
                    _avvio_consultazioni_sca = _avvio_consultazioni_sca.last()

                chiudi_azione(_avvio_consultazioni_sca)
                chiudi_azione(_verifica_vas, set_data=False)

                _avvio_consultazioni_sca = crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=STATO_AZIONE.necessaria
                    ))

                consultazione_vas = ConsultazioneVAS.objects\
                    .filter(procedura_vas=procedura_vas)\
                    .order_by('data_creazione')\
                    .first()
                consultazione_vas.data_avvio_consultazioni_sca = _avvio_consultazioni_sca.data
                consultazione_vas.save()

                procedura_vas.verifica_effettuata = True
                procedura_vas.save()

            else:
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TIPOLOGIA_AZIONE.avvio_esame_pareri_sca,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=STATO_AZIONE.necessaria
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _consultazione_vas = ConsultazioneVAS.objects.filter(
            procedura_vas=_procedura_vas).order_by('data_creazione').first()
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'SCA'):
            try:
                if _procedura_vas.risorse.filter(
                tipo='parere_sca', archiviata=False, user=info.context.user).count() == 0:
                    return GraphQLError(_("Forbidden"), code=403)

                _avvio_consultazioni_sca_count = _piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca).count()

                _pareri_vas_count = ParereVAS.objects.filter(
                    user=info.context.user,
                    procedura_vas=_procedura_vas,
                    consultazione_vas=_consultazione_vas
                )

                if _pareri_vas_count.count() == (_avvio_consultazioni_sca_count - 1):
                    _parere_vas = ParereVAS(
                        inviata=True,
                        user=info.context.user,
                        procedura_vas=_procedura_vas,
                        consultazione_vas=_consultazione_vas,
                    )
                    _parere_vas.save()
                elif _pareri_vas_count.count() != _avvio_consultazioni_sca_count:
                    return GraphQLError(_("Forbidden"), code=403)

                _tutti_pareri_inviati = True
                for _sca in _piano.soggetti_sca.all():
                    _pareri_vas_count = ParereVAS.objects.filter(
                        user=_sca.user,
                        procedura_vas=_procedura_vas,
                        consultazione_vas=_consultazione_vas
                    ).count()

                    if _pareri_vas_count != _avvio_consultazioni_sca_count:
                        _tutti_pareri_inviati = False
                        break

                if _tutti_pareri_inviati:

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="tutti_pareri_inviati")

                    cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

                return InvioPareriVAS(
                    vas_aggiornata=_procedura_vas,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class AvvioEsamePareriSCA(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.avvio_esame_pareri_sca

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _pareri_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_sca)
        if not isExecuted(_pareri_sca):
            return GraphQLError("Stato VAS incongruente", code=409)

        _avvio_esame_pareri_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_esame_pareri_sca)
        if needsExecution(_avvio_esame_pareri_sca):
            chiudi_azione(_avvio_esame_pareri_sca)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TIPOLOGIA_AZIONE.upload_elaborati_vas,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.necessaria
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        (rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune') or
         rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC')):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

                return AvvioEsamePareriSCA(
                    vas_aggiornata=_procedura_vas,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UploadElaboratiVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.upload_elaborati_vas

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):

        ensure_fase(fase, Fase.ANAGRAFICA)

        _upload_elaborati_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.upload_elaborati_vas)
        if needsExecution(_upload_elaborati_vas):
            chiudi_azione(_upload_elaborati_vas)

            _procedura_avvio = ProceduraAvvio.objects.filter(piano=piano).last()
            if not _procedura_avvio or _procedura_avvio.conclusa:
                piano.chiudi_pendenti(attesa=True, necessaria=False)
            procedura_vas.conclusa = True
            procedura_vas.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

                check_and_promote(_piano, info) # check for auto promotion

                return UploadElaboratiVAS(
                    vas_aggiornata=_procedura_vas,
                    errors=[]
                )

            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
