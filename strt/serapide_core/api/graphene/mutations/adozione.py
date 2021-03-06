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

from serapide_core.api.graphene.mutations.cartografica import inizializza_procedura_cartografica
from serapide_core.api.graphene.mutations.piano import check_and_promote, try_and_close_adozione
from serapide_core.helpers import update_create_instance

from serapide_core.api.piano_utils import (
    needs_execution,
    ensure_fase,
    chiudi_azione,
    crea_azione,
    get_scadenza, get_now,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    SoggettoOperante,
    ProceduraAdozione,
    ParereAdozioneVAS,
    ProceduraAdozioneVAS,
    RisorseAdozioneVas,
    Delega,

)

from serapide_core.modello.enums import (
    StatoAzione,
    TipologiaVAS,
    TipologiaAzione,
    TipoRisorsa,
    TipoExpire,
)

from serapide_core.api.graphene import (
    types, inputs)
from strt_users.enums import QualificaRichiesta, Qualifica

import serapide_core.api.auth.user as auth
from strt_users.models import Assegnatario

logger = logging.getLogger(__name__)


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

        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        for fixed_field in ['uuid', 'piano', 'data_creazione', 'ente']:
            if fixed_field in _procedura_adozione_data:
                logger.warning('Il campo "{}" non può essere modificato'.format(fixed_field))
                _procedura_adozione_data.pop(fixed_field)

        try:
            procedura_adozione_aggiornata = update_create_instance(_procedura_adozione, _procedura_adozione_data)

            # todo: impedire aggiornamenti burt se pubblicazione_burt eseguita

            if procedura_adozione_aggiornata.data_delibera_adozione:
                _expire_days = getattr(settings, 'ADOZIONE_RICEZIONE_PARERI_EXPIRE_DAYS', 30)
                _alert_delta = datetime.timedelta(days=_expire_days)
                procedura_adozione_aggiornata.data_ricezione_pareri = \
                    procedura_adozione_aggiornata.data_delibera_adozione + _alert_delta

            # todo: eliminare dal modello, la data viene calcolata su richiesta nel nodo di output
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


class TrasmissioneAdozione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):
        ensure_fase(fase, Fase.AVVIO)

        _trasmissione_adozione = piano.getFirstAction(TipologiaAzione.trasmissione_adozione)

        if needs_execution(_trasmissione_adozione):
            chiudi_azione(_trasmissione_adozione)

            inizializza_procedura_cartografica(_trasmissione_adozione)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return TrasmissioneAdozione(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class PubblicazioneBurt(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        ensure_fase(fase, Fase.AVVIO)

        pubblicazione_burt = piano.getFirstAction(TipologiaAzione.pubblicazione_burt)

        if needs_execution(pubblicazione_burt):
            chiudi_azione(pubblicazione_burt)

            now = get_now()

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.osservazioni_enti,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza((
                    now,  # ???
                    procedura_adozione.data_ricezione_osservazioni
                ))
            )

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.osservazioni_regione,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza((
                    now,  # ???
                    procedura_adozione.data_ricezione_osservazioni
                ))
            )

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.upload_osservazioni_privati,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza((
                    now,  # ???
                    procedura_adozione.data_ricezione_osservazioni
                ))
            )

            if procedura_adozione.pubblicazione_burt_data and \
                    piano.procedura_vas.tipologia != TipologiaVAS.NON_NECESSARIA:

                _procedura_adozione_vas, created = ProceduraAdozioneVAS.objects.get_or_create(piano=piano)

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.pareri_adozione_sca,
                        qualifica_richiesta=QualificaRichiesta.SCA,
                        stato=StatoAzione.ATTESA,
                    ).imposta_scadenza(
                        get_scadenza(
                            procedura_adozione.pubblicazione_burt_data,
                            TipoExpire.ADOZIONE_VAS_PARERI_SCA)
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        if not _procedura_adozione.pubblicazione_burt_url \
                or not _procedura_adozione.pubblicazione_burt_data \
                or not _procedura_adozione.pubblicazione_burt_bollettino \
                or not _procedura_adozione.pubblicazione_sito_url:
            return GraphQLError("Dati BURT non impostati", code=409)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return PubblicazioneBurt(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class OsservazioniRegione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        ensure_fase(fase, Fase.AVVIO)

        _osservazioni_regione = piano.getFirstAction(TipologiaAzione.osservazioni_regione)
        if needs_execution(_osservazioni_regione):
            chiudi_azione(_osservazioni_regione)

            if not piano.getFirstAction(TipologiaAzione.controdeduzioni):
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.controdeduzioni,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=StatoAzione.ATTESA
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return OsservazioniRegione(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class OsservazioniPrivati(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        ensure_fase(fase, Fase.AVVIO)

        _upload_osservazioni_privati = piano.getFirstAction(TipologiaAzione.upload_osservazioni_privati)
        if needs_execution(_upload_osservazioni_privati):
            chiudi_azione(_upload_osservazioni_privati)

            if not piano.getFirstAction(TipologiaAzione.controdeduzioni):
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.controdeduzioni,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=StatoAzione.ATTESA
                    ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return OsservazioniPrivati(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class Controdeduzioni(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        ensure_fase(fase, Fase.AVVIO)

        _controdeduzioni = piano.getFirstAction(TipologiaAzione.controdeduzioni)
        if needs_execution(_controdeduzioni):
            now = get_now()
            chiudi_azione(_controdeduzioni, now)

            for tipo in [TipologiaAzione.osservazioni_enti,
                         TipologiaAzione.osservazioni_regione,
                         TipologiaAzione.upload_osservazioni_privati]:
                oss = piano.getFirstAction(tipo)
                if needs_execution(oss):
                    chiudi_azione(oss, now)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.piano_controdedotto,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=StatoAzione.ATTESA
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return Controdeduzioni(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class PianoControdedotto(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.piano_controdedotto

    @staticmethod
    def procedura(piano):
        return piano.procedura_adozione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        _piano_controdedotto = piano.getFirstAction(TipologiaAzione.piano_controdedotto)

        if needs_execution(_piano_controdedotto):
            chiudi_azione(_piano_controdedotto)

            inizializza_procedura_cartografica(_piano_controdedotto)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return PianoControdedotto(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class EsitoConferenzaPaesaggistica(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.esito_conferenza_paesaggistica

    @staticmethod
    def procedura(piano):
        return piano.procedura_adozione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        _esito_cp = piano.getFirstAction(TipologiaAzione.esito_conferenza_paesaggistica)

        if needs_execution(_esito_cp):
            chiudi_azione(_esito_cp)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.rev_piano_post_cp,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=StatoAzione.NECESSARIA
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return EsitoConferenzaPaesaggistica(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class RevisionePianoPostConfPaesaggistica(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @staticmethod
    def action():
        return TipologiaAzione.rev_piano_post_cp

    @staticmethod
    def procedura(piano):
        return piano.procedura_adozione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        _rev_piano_post_cp = piano.getFirstAction(TipologiaAzione.rev_piano_post_cp)

        if needs_execution(_rev_piano_post_cp):
            chiudi_azione(_rev_piano_post_cp)

            inizializza_procedura_cartografica(_rev_piano_post_cp)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_adozione = ProceduraAdozione.objects.get(uuid=input['uuid'])
        _piano = _procedura_adozione.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return RevisionePianoPostConfPaesaggistica(
                adozione_aggiornata=_procedura_adozione,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class InvioPareriAdozioneVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraAdozioneVASNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        if not piano.procedura_vas or (piano.procedura_vas and piano.procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA):
            raise Exception("Tipologia VAS incongruente con l'azione richiesta")

        # TODO: controllare se possibile usare --> _pareri_sca = piano.getFirstAction(TIPOLOGIA_AZIONE.pareri_adozione_sca)
        _pareri_sca_list = piano.azioni(tipologia_azione=TipologiaAzione.pareri_adozione_sca)
        _pareri_sca = next((x for x in _pareri_sca_list if needs_execution(x)), None)

        if _pareri_sca:
            chiudi_azione(_pareri_sca)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.parere_motivato_ac,
                    qualifica_richiesta=QualificaRichiesta.AC,
                    stato=StatoAzione.ATTESA,
                ).imposta_scadenza(
                    get_scadenza(
                        procedura_adozione.pubblicazione_burt_data,
                        TipoExpire.ADOZIONE_VAS_PARERE_MOTIVATO_AC))
            )

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_ad_vas: ProceduraAdozioneVAS = ProceduraAdozioneVAS.objects.get(uuid=input['uuid'])
        _piano: Piano = _procedura_ad_vas.piano
        _procedura_adozione: ProceduraAdozione = ProceduraAdozione.objects.get(piano=_piano)

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.SCA):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            # controlla se l'utente ha caricato il suo file parere
            _esiste_risorsa = _procedura_ad_vas.risorse\
                    .filter(tipo=TipoRisorsa.PARERE_ADOZIONE_SCA.value, archiviata=False, user=info.context.user)\
                    .exists()
            if not _esiste_risorsa:
                logger.warning("RISORSA NON TROVATA per utente {}".format(info.context.user))
                for r in _procedura_ad_vas.risorse.filter(archiviata=False):
                    logger.warning('Risorsa {tipo} per utente {u}'.format(tipo=r.tipo, u=r.user))
                for r in RisorseAdozioneVas.objects.all():
                    logger.warning('RisorseAdozioneVas {tipo} per utente {u}'.format(tipo=r.risorsa.tipo, u=r.risorsa.user))

                return GraphQLError("File relativo al pareri SCA mancante", code=409)

            # controlla se l'utente ha già validato il parere
            _esiste_parere_ad_vas = ParereAdozioneVAS.objects\
                .filter(user=info.context.user, procedura_adozione=_procedura_adozione)\
                .exists()
            if _esiste_parere_ad_vas:
                return GraphQLError("Parere SCA esistente per questo utente")

            # ok, salva parere
            _parere_vas = ParereAdozioneVAS(
                inviata=True,
                user=info.context.user,
                procedura_adozione=_procedura_adozione
            )
            _parere_vas.save()

            # controlla se l'azione può essere chiusa
            _tutti_pareri_inviati = True
            for _so_sca in SoggettoOperante.get_by_qualifica(_piano, Qualifica.SCA):
                ass = Assegnatario.objects.filter(qualifica_ufficio=_so_sca.qualifica_ufficio)
                # todo aggiungi token
                utenti_sca = [a.utente for a in ass]
                _parere_sent = ParereAdozioneVAS.objects\
                    .filter(
                        procedura_adozione=_procedura_adozione,
                        user__in=utenti_sca)\
                    .exists()

                if not _parere_sent:
                    deleghe = Delega.objects.filter(delegante=_so_sca)
                    users = [d.token.user for d in deleghe]
                    _parere_sent = ParereAdozioneVAS.objects.filter(
                         procedura_adozione=_procedura_adozione,
                         user__in=users,
                    ).exists()

                if not _parere_sent:
                    _tutti_pareri_inviati = False
                    break

            if _tutti_pareri_inviati:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return InvioPareriAdozioneVAS(
                vas_aggiornata=_procedura_ad_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class InvioParereMotivatoAC(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraAdozioneVASNode)

    @staticmethod
    def action():
        return TipologiaAzione.parere_motivato_ac

    @staticmethod
    def procedura(piano):
        return piano.procedura_adozione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        if not piano.procedura_vas or (piano.procedura_vas and piano.procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA):
            raise Exception("Tipologia VAS incongruente con l'azione richiesta")

        _parere_motivato_ac = piano.getFirstAction(TipologiaAzione.parere_motivato_ac)

        if needs_execution(_parere_motivato_ac):
            chiudi_azione(_parere_motivato_ac)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.upload_elaborati_adozione_vas,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=StatoAzione.ATTESA
                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraAdozioneVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _procedura_adozione = ProceduraAdozione.objects.get(piano=_piano)

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.AC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        if not _procedura_adozione.pubblicazione_burt_data:
            return GraphQLError("Errore - burtdata mancante", code=500)

        try:
            # _tutti_pareri_inviati = True
            # for _sca in _piano.soggetti_sca.all():
            #     _pareri_vas_count = ParereAdozioneVAS.objects.filter(
            #         user=_sca.user,
            #         procedura_adozione=_procedura_adozione
            #     ).count()
            #
            #     if _pareri_vas_count == 0:
            #         _tutti_pareri_inviati = False
            #         break
            #
            # if _tutti_pareri_inviati:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)

            return InvioParereMotivatoAC(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadElaboratiAdozioneVAS(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    vas_aggiornata = graphene.Field(types.ProceduraAdozioneVASNode)

    @staticmethod
    def action():
        return TipologiaAzione.upload_elaborati_adozione_vas

    @staticmethod
    def procedura(piano):
        return piano.procedura_adozione

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_adozione, user):

        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.AVVIO)

        if not piano.procedura_vas or (piano.procedura_vas and piano.procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA):
            raise Exception("Tipologia VAS incongruente con l'azione richiesta")

        _upload_elaborati_adozione_vas = piano.getFirstAction(TipologiaAzione.upload_elaborati_adozione_vas)

        if needs_execution(_upload_elaborati_adozione_vas):
            chiudi_azione(_upload_elaborati_adozione_vas)

            _procedura_adozione_vas = ProceduraAdozioneVAS.objects.filter(piano=piano).last()
            _procedura_adozione_vas.conclusa = True
            _procedura_adozione_vas.save()

            try_and_close_adozione(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_vas = ProceduraAdozioneVAS.objects.get(uuid=input['uuid'])
        _piano = _procedura_vas.piano
        _procedura_adozione = ProceduraAdozione.objects.get(piano=_piano)

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        if not _procedura_adozione.pubblicazione_burt_data:
            return GraphQLError("Errore - burtdata mancante", code=500)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_adozione, info.context.user)
            check_and_promote(_piano, info)

            return UploadElaboratiAdozioneVAS(
                vas_aggiornata=_procedura_vas,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)
