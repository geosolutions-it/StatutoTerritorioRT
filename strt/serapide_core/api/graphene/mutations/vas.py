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

from graphene import relay
from graphql_extensions.exceptions import GraphQLError

from django.utils import timezone

from serapide_core.api.graphene.mutations.piano import (
    check_and_promote,
    try_and_close_avvio,

)

from serapide_core.api.piano_utils import (
    needs_execution,
    is_executed,
    ensure_fase,
    chiudi_azione,
    crea_azione, get_scadenza, get_now,
)

from serapide_core.helpers import (
    update_create_instance
)

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
    ParereVerificaVAS,
    SoggettoOperante,
    Delega,

)
from serapide_core.modello.enums import (
    Fase,
    StatoAzione,
    TipologiaVAS,
    TipologiaAzione,
    TipoRisorsa,
    TipoExpire,
    TipoMail,
)

from strt_users.enums import QualificaRichiesta, Qualifica

from serapide_core.api.graphene import (types, inputs)
import serapide_core.api.auth.user as auth

from strt_users.models import (
    Assegnatario,
    Utente,
)

logger = logging.getLogger(__name__)


def init_vas_procedure(piano: Piano, utente: Utente):

    procedura_vas = piano.procedura_vas
    _selezione_tipologia_vas = piano.getFirstAction(TipologiaAzione.selezione_tipologia_vas)

    now = get_now()

    if needs_execution(_selezione_tipologia_vas):
        chiudi_azione(_selezione_tipologia_vas, now)
    else:
        raise GraphQLError("Stato inconsistente nell'inizializzazione VAS", code=500)

    if procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
        pass

    elif procedura_vas.tipologia == TipologiaVAS.PROCEDURA_ORDINARIA:

        crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.invio_doc_preliminare,
                qualifica_richiesta=QualificaRichiesta.COMUNE,
                stato=StatoAzione.ATTESA,
            ))

    elif procedura_vas.tipologia == TipologiaVAS.VERIFICA:

        crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.trasmissione_dpv_vas,
                qualifica_richiesta=QualificaRichiesta.AC,
                stato=StatoAzione.ATTESA,
            ).imposta_scadenza(
                get_scadenza(now, TipoExpire.TRASMISSIONE_DPV_VAS)
            )
        )

    elif procedura_vas.tipologia == TipologiaVAS.VERIFICA_SEMPLIFICATA:

        crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.emissione_provvedimento_verifica,
                qualifica_richiesta=QualificaRichiesta.AC,
                stato=StatoAzione.ATTESA,
            ).imposta_scadenza(
                get_scadenza(now, TipoExpire.EMISSIONE_PV_VERIFICASEMPLIFICATA)
            )
        )

    elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO:

        crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.pareri_verifica_sca,
                qualifica_richiesta=QualificaRichiesta.SCA,
                stato=StatoAzione.ATTESA,
            ).imposta_scadenza(
                get_scadenza(now, TipoExpire.PARERI_VERIFICA_SCA_PROCEDIMENTOSEMPLIFICATO)
            )
        )

        # AC deve essere notificato
        piano_phase_changed.send(
            message_type=TipoMail.trasmissione_dp_vas,
            sender=Piano,
            piano=piano,
            user=utente,
        )

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

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        _ente = _piano.ente

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
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.OPCOM):
                    if _tipologia:  #  and _tipologia in TipologiaVAS:
                        _tipo_parsed = TipologiaVAS.fix_enum(_tipologia, none_on_error=True)
                        if not _tipo_parsed:
                            return GraphQLError("Tipologia non riconosciuta [{}]".format(_tipologia), code=400)
                        _procedura_vas_data['tipologia'] = _tipo_parsed
                else:
                    logger.info('Non si hanno i privilegi per modificare il campo "tipologia"')

            # Note (O)
            if 'note' in _procedura_vas_data:
                _data = _procedura_vas_data.pop('note')
                if auth.has_qualifica(info.context.user, _piano.ente, Qualifica.OPCOM):
                    _procedura_vas.note = _data[0]
                else:
                    logger.info('Non si hanno i privilegi per modificare il campo "note"')

            # perform check before update
            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ap:
                if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.OPCOM):
                    return GraphQLError("Forbidden - Non è permesso modificare un campo AP", code=403)
                if is_executed(_piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ap)):
                    return GraphQLError("Il campo pubblicazione provvedimento è bloccato ", code=403)

            # perform check before update
            if _procedura_vas_data.pubblicazione_provvedimento_verifica_ac:
                if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
                    return GraphQLError("Forbidden - Non è permesso modificare un campo AC", code=403)
                if is_executed(_piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ac)):
                    return GraphQLError("Il campo pubblicazione provvedimento è bloccato ", code=403)

            # update!
            procedura_vas_aggiornata = update_create_instance(_procedura_vas, _procedura_vas_data)

            return cls(procedura_vas_aggiornata=procedura_vas_aggiornata)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class TrasmissioneDPVVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _pareri_verifica_vas = piano.getFirstAction(TipologiaAzione.trasmissione_dpv_vas)
        if needs_execution(_pareri_verifica_vas):
            now = get_now()
            chiudi_azione(_pareri_verifica_vas, now)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.pareri_verifica_sca,
                    qualifica_richiesta=QualificaRichiesta.SCA,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza(
                    get_scadenza(now, TipoExpire.PARERI_VERIFICA_SCA)
                )
            )

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            if not _procedura_vas.risorse \
                    .filter(tipo=TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS.value, archiviata=False) \
                    .exists():
                return GraphQLError("File mancante: {}".format(TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS.value), code=409)

            if not SoggettoOperante.get_by_qualifica(_piano, Qualifica.SCA).exists() and \
                    not Delega.objects.filter(qualifica=Qualifica.SCA, delegante__piano=_piano).exists():
                return GraphQLError("Non sono associati SCA al piano", code=409)

            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return InvioPareriVerificaVAS(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
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
        return TipologiaAzione.pareri_verifica_sca

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        if procedura_vas.tipologia == TipologiaVAS.VERIFICA:
            exp = TipoExpire.EMISSIONE_PV_VERIFICA
        elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO:
            exp = TipoExpire.EMISSIONE_PV_PROCEDIMENTOSEMPLIFICATO
        else:
            raise GraphQLError("Tipo procedura VAS inaspettata: {}".format(procedura_vas.tipologia), code=403)

        _pareri_verifica_vas = piano.getFirstAction(TipologiaAzione.pareri_verifica_sca)
        if needs_execution(_pareri_verifica_vas):
            chiudi_azione(_pareri_verifica_vas)

            _azione_start_vas = piano.getFirstAction(TipologiaAzione.selezione_tipologia_vas)
            _data_start_vas = _azione_start_vas.data

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.emissione_provvedimento_verifica,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza(
                    get_scadenza(_data_start_vas, exp)
                )
            )

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.SCA):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:

            if not _procedura_vas.risorse\
                    .filter(tipo=TipoRisorsa.PARERE_VERIFICA_VAS.value, archiviata=False, user=info.context.user)\
                    .exists():
                return GraphQLError("File mancante: {}".format(TipoRisorsa.PARERE_VERIFICA_VAS.value), code=409)

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

                assegnatari = Assegnatario.objects.filter(qualifica_ufficio=_sca.qualifica_ufficio)
                users = [a.utente for a in assegnatari]
                _pareri_vas_exists = ParereVerificaVAS.objects.filter(
                    procedura_vas=_procedura_vas,
                    user__in=users,
                ).exists()

                if not _pareri_vas_exists:
                    deleghe = Delega.objects.filter(delegante=_sca, qualifica=Qualifica.SCA)
                    users = [d.token.user for d in deleghe]
                    _pareri_vas_exists = ParereVerificaVAS.objects.filter(
                         procedura_vas=_procedura_vas,
                         user__in=users,
                    ).exists()

                if not _pareri_vas_exists:
                    _tutti_pareri_inviati = False
                    break

            if _tutti_pareri_inviati:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return InvioPareriVerificaVAS(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class EmissioneProvvedimentoVerifica(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _epv = piano.getFirstAction(TipologiaAzione.emissione_provvedimento_verifica)
        if needs_execution(_epv):
            now = get_now()
            chiudi_azione(_epv, now)

            procedura_vas.data_assoggettamento = now
            procedura_vas.verifica_effettuata = True
            procedura_vas.save()

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.pubblicazione_provvedimento_verifica_ac,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=StatoAzione.NECESSARIA,
                ))

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.pubblicazione_provvedimento_verifica_ap,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=StatoAzione.NECESSARIA,
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            if not _procedura_vas.risorse\
                    .filter(tipo=TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS.value, archiviata=False)\
                    .exists():
                return GraphQLError("File mancante: {}".format(TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS.value), code=409)

            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return EmissioneProvvedimentoVerifica(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


def check_join_pubblicazione_provvedimento(info, piano: Piano):

    pp_ap = piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ap)
    pp_ac = piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ac)

    if is_executed(pp_ap) and is_executed(pp_ac):

        _vas: ProceduraVAS = piano.procedura_vas

        if not _vas.assoggettamento:
            _vas.conclusa = True
            _vas.save()

            if try_and_close_avvio(piano):
                check_and_promote(piano, info)

        else:
            if _vas.tipologia == TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO:
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.redazione_documenti_vas,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=StatoAzione.NECESSARIA
                    ))
            else:
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.invio_doc_preliminare,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=StatoAzione.NECESSARIA
                    ))


class PubblicazioneProvvedimentoVerificaAp(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, info):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _ppv = piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ap)
        if needs_execution(_ppv):
            chiudi_azione(_ppv)

            check_join_pubblicazione_provvedimento(info, piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        if not _procedura_vas.pubblicazione_provvedimento_verifica_ap:
            return GraphQLError("URL di pubblicazione non impostata", code=409)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info)

            return PubblicazioneProvvedimentoVerificaAp(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class PubblicazioneProvvedimentoVerificaAc(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, info):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _ppv = piano.getFirstAction(TipologiaAzione.pubblicazione_provvedimento_verifica_ac)
        if needs_execution(_ppv):
            chiudi_azione(_ppv)

            check_join_pubblicazione_provvedimento(info, piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        if not _procedura_vas.pubblicazione_provvedimento_verifica_ac:
            return GraphQLError("URL di pubblicazione non impostata", code=409)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info)

            return PubblicazioneProvvedimentoVerificaAc(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class InvioDocPreliminare(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):

        ensure_fase(fase, Fase.ANAGRAFICA)

        _invio_doc_preliminare = piano.getFirstAction(TipologiaAzione.invio_doc_preliminare)
        if needs_execution(_invio_doc_preliminare):
            now = get_now()
            chiudi_azione(_invio_doc_preliminare, now)

            crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.trasmissione_pareri_sca,
                        qualifica_richiesta=QualificaRichiesta.SCA,
                        stato=StatoAzione.ATTESA,
                    ).imposta_scadenza(
                        get_scadenza(now, TipoExpire.TRASMISSIONE_PARERI_SCA)
                    )
            )

            crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.trasmissione_pareri_ac,
                        qualifica_richiesta=QualificaRichiesta.AC,
                        stato=StatoAzione.ATTESA
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        # check generico sul piano
        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        # check specifico azione
        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        # check risorsa
        if not _procedura_vas.risorse\
                .filter(tipo=TipoRisorsa.DOCUMENTO_PRELIMINARE_VAS.value, archiviata=False, user=info.context.user)\
                .exists():
            return GraphQLError("Risorsa mancante: {}".format(TipoRisorsa.DOCUMENTO_PRELIMINARE_VAS.value), code=409)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return InvioDocPreliminare(
                procedura_vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


def check_join_redazione_documenti_vas(user, piano: Piano):

    tp_sca = piano.getFirstAction(TipologiaAzione.trasmissione_pareri_sca)
    tp_ac = piano.getFirstAction(TipologiaAzione.trasmissione_pareri_ac)

    if is_executed(tp_sca) and is_executed(tp_ac):
        crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.redazione_documenti_vas,
                qualifica_richiesta=QualificaRichiesta.COMUNE,
                stato=StatoAzione.NECESSARIA
            ))

        return True

    return False


class TrasmissionePareriSCA(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TipologiaAzione.trasmissione_pareri_sca

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _azione = piano.getFirstAction(TipologiaAzione.trasmissione_pareri_sca)

        if needs_execution(_azione):
            chiudi_azione(_azione)

        check_join_redazione_documenti_vas(user, piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.SCA):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            errs = []

            if not _procedura_vas.risorse\
                    .filter(tipo=TipoRisorsa.PARERE_SCA.value, archiviata=False, user=info.context.user)\
                    .exists():
                return GraphQLError("File relativo al pareri SCA mancante", code=409)

            # attenzione: se ci sono più utenti collegati ad uno stesso SO SCA, con questo controllo ognuno
            # puo caricare il proprio parere.
            _esiste_parere = ParereVAS.objects.filter(
                user=info.context.user,
                procedura_vas=_procedura_vas).exists()

            if not _esiste_parere:
                _parere_vas = ParereVAS(
                    inviata=True,
                    user=info.context.user,
                    procedura_vas=_procedura_vas,
                )
                _parere_vas.save()

            # controlliamo se tutti gli SCA associati al piano hanno dato parere
            _tutti_pareri_inviati = True
            for _so_sca in SoggettoOperante.get_by_qualifica(_piano, Qualifica.SCA):
                # controlla invio per assegnatari
                ass = Assegnatario.objects.filter(qualifica_ufficio=_so_sca.qualifica_ufficio)
                utenti_sca = {a.utente for a in ass}

                deleghe = Delega.objects.filter(delegante=_so_sca, qualifica=Qualifica.SCA)
                utenti_sca |= {d.token.user for d in deleghe if d.token.user is not None}

                _esiste_parere_sca = ParereVAS.objects\
                    .filter(
                        procedura_vas=_procedura_vas,
                        user__in=utenti_sca)\
                    .exists()

                if not _esiste_parere_sca:
                    _tutti_pareri_inviati = False
                    errs.append('Parere mancante da {}'.format(_so_sca.qualifica_ufficio.ufficio))
                    # non si effettua il break, così avremo la lista di tutti gli SCA mancanti

            if _tutti_pareri_inviati:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return TrasmissionePareriSCA(
                vas_aggiornata=_procedura_vas,
                errors=errs
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class TrasmissionePareriAC(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TipologiaAzione.trasmissione_pareri_ac

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _azione = piano.getFirstAction(TipologiaAzione.trasmissione_pareri_ac)

        if needs_execution(_azione):
            chiudi_azione(_azione)

        check_join_redazione_documenti_vas(user, piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            errs = []

            if not _procedura_vas.risorse\
                    .filter(tipo=TipoRisorsa.PARERE_AC.value, archiviata=False, user=info.context.user)\
                    .exists():
                return GraphQLError("File relativo al pareri AC mancante", code=409)

            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            return TrasmissionePareriAC(
                vas_aggiornata=_procedura_vas,
                errors=errs
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class RedazioneDocumentiVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @staticmethod
    def action():
        return TipologiaAzione.redazione_documenti_vas

    @staticmethod
    def procedura(piano):
        return piano.procedura_vas

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _azione = piano.getFirstAction(TipologiaAzione.redazione_documenti_vas)

        if needs_execution(_azione):
            chiudi_azione(_azione)

        procedura_vas.conclusa = True
        procedura_vas.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            errs = []

            for tipo in [TipoRisorsa.RAPPORTO_AMBIENTALE, TipoRisorsa.SINTESI_NON_TECNICA]:
                if not _procedura_vas.risorse\
                        .filter(tipo=tipo.value, archiviata=False, user=info.context.user)\
                        .exists():
                    return GraphQLError("File mancante: {}".format(tipo.value), code=409)

            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            if try_and_close_avvio(_piano):
                check_and_promote(_piano, info)  # check for auto promotion

            return RedazioneDocumentiVAS(
                vas_aggiornata=_procedura_vas,
                errors=errs
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)

