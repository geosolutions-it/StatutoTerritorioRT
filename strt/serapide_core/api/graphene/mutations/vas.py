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

    isExecuted,
    needsExecution,
    ensure_fase,
    crea_azione,
    chiudi_azione,
)
from strt_users.enums import QualificaRichiesta, Qualifica
from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TipologiaVAS,
    TIPOLOGIA_AZIONE,
    # TIPOLOGIA_ATTORE,
)

from serapide_core.api.graphene import (types, inputs)
from serapide_core.api.graphene.mutations import fase

import serapide_core.api.auth.user as auth


logger = logging.getLogger(__name__)


def init_vas_procedure(piano:Piano):

    # _order = piano.azioni.count()
    _order = Azione.count_by_piano(piano)
    procedura_vas = piano.procedura_vas
    _verifica_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_verifica_vas)

    if _verifica_vas:
        if procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
            _verifica_vas.stato = STATO_AZIONE.nessuna

        elif procedura_vas.tipologia in \
                (TipologiaVAS.PROCEDIMENTO,
                 TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO):

            _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
            chiudi_azione(_verifica_vas, datetime.datetime.now(timezone.get_current_timezone()) + \
                                 datetime.timedelta(days=_verifica_vas_expire_days))

            _avvio_consultazioni_sca_ac_expire_days = 10
            crea_azione(Azione(
                piano=piano,
                tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                qualifica_richiesta=QualificaRichiesta.AC,
                order=_order,
                stato=STATO_AZIONE.attesa,
                data=datetime.datetime.now(timezone.get_current_timezone()) +
                     datetime.timedelta(days=_avvio_consultazioni_sca_ac_expire_days)
            ))

        elif procedura_vas.tipologia == TipologiaVAS.SEMPLIFICATA:
            _verifica_vas.stato = STATO_AZIONE.nessuna

            _emissione_provvedimento_verifica_expire_days = 30
            crea_azione(Azione(
                piano=piano,
                tipologia=TIPOLOGIA_AZIONE.emissione_provvedimento_verifica,
                qualifica_richiesta=QualificaRichiesta.AC,
                order=_order,
                stato=STATO_AZIONE.attesa,
                data=datetime.datetime.now(timezone.get_current_timezone()) +
                     datetime.timedelta(days=_emissione_provvedimento_verifica_expire_days)
            ))

        elif procedura_vas.tipologia == TipologiaVAS.VERIFICA:
            # _verifica_vas.stato = STATO_AZIONE.attesa
            _verifica_vas.stato = STATO_AZIONE.nessuna
            _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
            _verifica_vas.data = datetime.datetime.now(timezone.get_current_timezone()) + \
                                 datetime.timedelta(days=_verifica_vas_expire_days)

            _pareri_vas_expire_days = getattr(settings, 'PARERI_VERIFICA_VAS_EXPIRE_DAYS', 30)
            _pareri_sca = Azione(
                tipologia=TIPOLOGIA_AZIONE.pareri_verifica_sca,
                attore=TIPOLOGIA_ATTORE.sca,
                order=_order,
                stato=STATO_AZIONE.attesa,
                data=datetime.datetime.now(timezone.get_current_timezone()) +
                     datetime.timedelta(days=_pareri_vas_expire_days)
            )
            _pareri_sca.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_pareri_sca, piano=piano)

            _emissione_provvedimento_verifica_expire_days = 90
            _emissione_provvedimento_verifica = Azione(
                tipologia=TIPOLOGIA_AZIONE.emissione_provvedimento_verifica,
                attore=TIPOLOGIA_ATTORE.ac,
                order=_order,
                stato=STATO_AZIONE.attesa,
                data=datetime.datetime.now(timezone.get_current_timezone()) +
                     datetime.timedelta(days=_emissione_provvedimento_verifica_expire_days)
            )
            _emissione_provvedimento_verifica.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_emissione_provvedimento_verifica, piano=piano)

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

            procedura_vas_aggiornata = update_create_instance(_procedura_vas, _procedura_vas_data)

            if procedura_vas_aggiornata.pubblicazione_provvedimento_verifica_ap:
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
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

            if procedura_vas_aggiornata.pubblicazione_provvedimento_verifica_ac:
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP) or \
                    auth.is_soggetto_operante(info.context.user, _piano, Qualifica.AC):

                    _pubblicazione_provvedimento_verifica_ac = _piano.getFirstAction(
                            TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                            qualifica_richiesta=QualificaRichiesta.AC)

                    if needsExecution(_pubblicazione_provvedimento_verifica_ac):
                        chiudi_azione(_pubblicazione_provvedimento_verifica_ac.stato, set_data=False)

                        # Notify Users
                        piano_phase_changed.send(
                            sender=Piano,
                            user=info.context.user,
                            piano=_piano,
                            message_type="piano_verifica_vas_updated")


            if procedura_vas_aggiornata.pubblicazione_provvedimento_verifica_ap and \
                procedura_vas_aggiornata.pubblicazione_provvedimento_verifica_ac:

                _procedura_avvio = ProceduraAvvio.objects.filter(piano=_piano).last()
                if not _procedura_avvio or _procedura_avvio.conclusa:
                    _piano.chiudi_pendenti(attesa=True, necessaria=False)
                procedura_vas_aggiornata.conclusa = True
                procedura_vas_aggiornata.save()

                if _piano.is_eligible_for_promotion:
                    _piano.fase = _fase = Fase.objects.get(nome=_piano.next_phase)
                    _piano.save()

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    fase.promuovi_piano(_fase, _piano)

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
        return TIPOLOGIA_AZIONE.pareri_verifica_sca

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)
        # Update Azioni Piano
        # - Update Action state accordingly
        _pareri_verifica_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_verifica_sca)
        if _pareri_verifica_sca.stato == STATO_AZIONE.attesa:
            _pareri_verifica_sca.stato = STATO_AZIONE.nessuna
            _pareri_verifica_sca.data = datetime.datetime.now(timezone.get_current_timezone())
            _pareri_verifica_sca.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'SCA'):
            try:
                _pareri_vas_count = ParereVerificaVAS.objects.filter(
                    user=info.context.user,
                    procedura_vas=_procedura_vas
                )

                if _pareri_vas_count.count() == 0:
                    _parere_vas = ParereVerificaVAS(
                        inviata=True,
                        user=info.context.user,
                        procedura_vas=_procedura_vas
                    )
                    _parere_vas.save()
                elif _pareri_vas_count.count() != 1:
                    return GraphQLError(_("Forbidden"), code=403)

                _tutti_pareri_inviati = True
                for _sca in _piano.soggetti_sca.all():
                    _pareri_vas_count = ParereVerificaVAS.objects.filter(
                        user=_sca.user,
                        procedura_vas=_procedura_vas
                    ).count()
                    if _pareri_vas_count != 1:
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
        else:
            return GraphQLError(_("Forbidden"), code=403)


class AssoggettamentoVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas):
        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        ensure_fase(fase, Fase.ANAGRAFICA)

        # - Update Action state accordingly
        if procedura_vas.assoggettamento:
            _avvio_consultazioni_sca = Azione(
                tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                attore=TIPOLOGIA_ATTORE.comune,
                order=_order,
                stato=STATO_AZIONE.necessaria
            )
            _avvio_consultazioni_sca.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_avvio_consultazioni_sca, piano=piano)

            procedura_vas.verifica_effettuata = True
            procedura_vas.data_assoggettamento = datetime.datetime.now(timezone.get_current_timezone())
            procedura_vas.save()
        else:
            _pubblicazione_vas_comune = Azione(
                tipologia=TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                attore=TIPOLOGIA_ATTORE.comune,
                order=_order,
                stato=STATO_AZIONE.necessaria
            )
            _pubblicazione_vas_comune.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_pubblicazione_vas_comune, piano=piano)

            _pubblicazione_vas_ac = Azione(
                tipologia=TIPOLOGIA_AZIONE.pubblicazione_provvedimento_verifica,
                attore=TIPOLOGIA_ATTORE.ac,
                order=_order,
                stato=STATO_AZIONE.necessaria
            )
            _pubblicazione_vas_ac.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_pubblicazione_vas_ac, piano=piano)
            procedura_vas.non_necessaria = True
            procedura_vas.verifica_effettuata = True
            procedura_vas.save()

        if procedura_vas.verifica_effettuata:
            _emissione_provvedimento_verifica = piano.getFirstAction(TIPOLOGIA_AZIONE.emissione_provvedimento_verifica)
            if needsExecution(_emissione_provvedimento_verifica):
                _emissione_provvedimento_verifica.stato = STATO_AZIONE.nessuna
                _emissione_provvedimento_verifica.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'AC'):
            try:
                _pareri_verifica_sca = _piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_verifica_sca)
                if needsExecution(_pareri_verifica_sca):
                    return GraphQLError(_("Forbidden"), code=403)
                if not _procedura_vas.verifica_effettuata and \
                _procedura_vas.tipologia in (TipologiaVAS.VERIFICA, TipologiaVAS.SEMPLIFICATA):
                    cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas)
                else:
                    return GraphQLError(_("Forbidden"), code=403)

                return AssoggettamentoVAS(
                    vas_aggiornata=_procedura_vas,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


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

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        ensure_fase(fase, Fase.ANAGRAFICA)

        # - Update Action state accordingly
        _avvio_consultazioni_sca = piano.azioni.filter(
            tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca)
        for _ac in _avvio_consultazioni_sca:
            if _ac.stato != STATO_AZIONE.nessuna:
                _avvio_consultazioni_sca = _ac
                break
        if _avvio_consultazioni_sca and \
            not isinstance(_avvio_consultazioni_sca, QuerySet) and \
            _avvio_consultazioni_sca.stato != STATO_AZIONE.nessuna:

            _avvio_consultazioni_sca.stato = STATO_AZIONE.nessuna
            _avvio_consultazioni_sca.data = datetime.datetime.now(timezone.get_current_timezone())

            consultazione_vas.data_avvio_consultazioni_sca = _avvio_consultazioni_sca.data

            _avvio_consultazioni_sca.save()
            consultazione_vas.save()

            _pareri_vas_expire_days = getattr(settings, 'PARERI_VAS_EXPIRE_DAYS', 60)
            _pareri_sca = Azione(
                tipologia=TIPOLOGIA_AZIONE.pareri_sca,
                attore=TIPOLOGIA_ATTORE.sca,
                order=_order,
                stato=STATO_AZIONE.attesa,
                data=datetime.datetime.now(timezone.get_current_timezone()) +
                datetime.timedelta(days=_pareri_vas_expire_days)
            )
            _pareri_sca.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_pareri_sca, piano=piano)

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
        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        ensure_fase(fase, Fase.ANAGRAFICA)

        # - Update Action state accordingly
        _verifica_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_verifica_vas)

        _avvio_consultazioni_sca = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca)
        for _ac in _avvio_consultazioni_sca:
            if _ac.stato != STATO_AZIONE.nessuna:
                _avvio_consultazioni_sca = _ac
                break

        _pareri_sca = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.pareri_sca)
        for _psca in _pareri_sca:
            if _psca.stato != STATO_AZIONE.nessuna:
                _pareri_sca = _psca
                break

        if _verifica_vas and \
        _pareri_sca and \
        (isinstance(_pareri_sca, QuerySet) or
         _pareri_sca.stato != STATO_AZIONE.nessuna):
            if isinstance(_pareri_sca, QuerySet):
                _pareri_sca = _pareri_sca.last()

            _pareri_sca.stato = STATO_AZIONE.nessuna
            _pareri_sca.data = datetime.datetime.now(timezone.get_current_timezone())
            _pareri_sca.save()

            if _avvio_consultazioni_sca and \
               (not isinstance(_avvio_consultazioni_sca, QuerySet) or
                  ((_avvio_consultazioni_sca.count() == 1 and
                    procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO) or
                   (_avvio_consultazioni_sca.count() == 1 and
                    _avvio_consultazioni_sca.first().attore == TIPOLOGIA_ATTORE.ac and
                    procedura_vas.tipologia != TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO))):

                if isinstance(_avvio_consultazioni_sca, QuerySet):
                    _avvio_consultazioni_sca = _avvio_consultazioni_sca.last()

                _avvio_consultazioni_sca.stato = STATO_AZIONE.nessuna
                _avvio_consultazioni_sca.data = datetime.datetime.now(timezone.get_current_timezone())
                _avvio_consultazioni_sca.save()

                _verifica_vas.stato = STATO_AZIONE.nessuna
                _verifica_vas.save()

                _avvio_consultazioni_sca = Azione(
                    tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.necessaria
                )
                _avvio_consultazioni_sca.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_avvio_consultazioni_sca, piano=piano)

                consultazione_vas = ConsultazioneVAS.objects.filter(
                    procedura_vas=procedura_vas).order_by('data_creazione').first()
                consultazione_vas.data_avvio_consultazioni_sca = _avvio_consultazioni_sca.data
                consultazione_vas.save()

                procedura_vas.verifica_effettuata = True
                procedura_vas.save()

            else:
                _avvio_esame_pareri_sca = Azione(
                    tipologia=TIPOLOGIA_AZIONE.avvio_esame_pareri_sca,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.necessaria
                )
                _avvio_esame_pareri_sca.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_avvio_esame_pareri_sca, piano=piano)

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

        # Update Azioni Piano
        # - Complete Current Actions
        _order = piano.azioni.count()

        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA)
        _pareri_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_sca)
        if isExecuted(_pareri_sca):

            _avvio_esame_pareri_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_esame_pareri_sca)

            if needsExecution(_avvio_esame_pareri_sca):
                _avvio_esame_pareri_sca.stato = STATO_AZIONE.nessuna
                _avvio_esame_pareri_sca.data = datetime.datetime.now(timezone.get_current_timezone())
                _avvio_esame_pareri_sca.save()

                _upload_elaborati_vas = Azione(
                    tipologia=TIPOLOGIA_AZIONE.upload_elaborati_vas,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.necessaria
                )
                _upload_elaborati_vas.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_upload_elaborati_vas, piano=piano)

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

        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA)

        _upload_elaborati_vas = piano.getFirstAction(TIPOLOGIA_AZIONE.upload_elaborati_vas)
        if needsExecution(_upload_elaborati_vas):
            _upload_elaborati_vas.stato = STATO_AZIONE.nessuna
            _upload_elaborati_vas.data = datetime.datetime.now(timezone.get_current_timezone())
            _upload_elaborati_vas.save()

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

                if _piano.is_eligible_for_promotion:
                    _piano.fase = _fase = Fase.objects.get(nome=_piano.next_phase)
                    _piano.save()

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    fase.promuovi_piano(_fase, _piano)

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
