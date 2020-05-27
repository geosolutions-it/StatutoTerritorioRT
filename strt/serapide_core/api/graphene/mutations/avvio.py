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

from django.utils import timezone

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.api.graphene.mutations import log_enter_mutate

from serapide_core.helpers import (
    update_create_instance
)

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    QualificaRichiesta,
    Piano,
    Azione,
    SoggettoOperante,
    ProceduraVAS,
    ProceduraAvvio,
    ConferenzaCopianificazione,
)

from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TipologiaAzione,
    TipologiaCopianificazione,
    TipoRisorsa,
)

from serapide_core.api.graphene import (types, inputs)
from serapide_core.api.graphene.mutations.vas import init_vas_procedure
from serapide_core.api.graphene.mutations.piano import check_and_promote, try_and_close_avvio
from serapide_core.api.piano_utils import (
    needs_execution,
    is_executed,
    ensure_fase,
    chiudi_azione,
    crea_azione, get_now,
)
import serapide_core.api.auth.user as auth
from strt_users.enums import Qualifica

logger = logging.getLogger(__name__)


class UpdateProceduraAvvio(relay.ClientIDMutation):

    class Input:
        procedura_avvio = graphene.Argument(inputs.ProceduraAvvioUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _procedura_avvio_data = input.get('procedura_avvio')

        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        for fixed_field in ['uuid', 'piano', 'data_creazione', 'ente']:
            if fixed_field in _procedura_avvio_data:
                logger.warning('Il campo "{}" non può essere modificato'.format(fixed_field))
                _procedura_avvio_data.pop(fixed_field)

        try:
            # Tipologia (O)
            if 'conferenza_copianificazione' in _procedura_avvio_data:
                if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.OPCOM):
                    return GraphQLError("Forbidden - Richiesta qualifica Responsabile", code=403)

                _conferenza_copianificazione = TipologiaCopianificazione.fix_enum(
                    _procedura_avvio_data.pop('conferenza_copianificazione'), none_on_error=True)

                if _conferenza_copianificazione:
                    _procedura_avvio_data['conferenza_copianificazione'] = _conferenza_copianificazione

            procedura_avvio_aggiornata = update_create_instance(_procedura_avvio, _procedura_avvio_data)

            return cls(procedura_avvio_aggiornata=procedura_avvio_aggiornata)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class AvvioPiano(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def autorita_ok(cls, piano, qualifiche):
        if not piano.soggetto_proponente:
            return False

        for qualifica in qualifiche:
            c = SoggettoOperante.get_by_qualifica(piano, qualifica=qualifica).count()
            if c > 0:
                return True;

        return False

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA);

        _avvio_procedimento = piano.getFirstAction(TipologiaAzione.avvio_procedimento)
        if needs_execution(_avvio_procedimento):
            if not cls.autorita_ok(piano, [Qualifica.GC]):
                raise GraphQLError("Genio Civile non trovato tra i soggetti operanti", code=400)

            if not cls.autorita_ok(piano, [Qualifica.PIAN, Qualifica.URB]):
                raise GraphQLError("Pianificazione o Urbanistica non trovato tra i soggetti operanti", code=400)

            if procedura_avvio.conferenza_copianificazione is None:
                raise GraphQLError("Conferenza copianificazione non impostata", code=400)

            chiudi_azione(_avvio_procedimento)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.contributi_tecnici,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=STATO_AZIONE.attesa,
                ).imposta_scadenza((
                    get_now(),  # ??
                    procedura_avvio.data_scadenza_risposta
                ))
            )

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.selezione_tipologia_vas,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.attesa
                ))

            init_vas_procedure(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="contributi_tecnici")

            return AvvioPiano(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )

        except GraphQLError as e:
            return e

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class FormazionePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):

        ensure_fase(fase, Fase.ANAGRAFICA);

        _formazione_del_piano = piano.getFirstAction(TipologiaAzione.formazione_del_piano)
        if needs_execution(_formazione_del_piano):
            chiudi_azione(_formazione_del_piano)

            try_and_close_avvio(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas = ProceduraVAS.objects.get(piano=_piano)

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

            check_and_promote(_piano, info)

            return FormazionePiano(
                piano_aggiornato=_piano,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class ContributiTecnici(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TipologiaAzione.contributi_tecnici

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_procedimento = piano.getFirstAction(TipologiaAzione.avvio_procedimento)
        _contributi_tecnici = piano.getFirstAction(TipologiaAzione.contributi_tecnici)

        if is_executed(_avvio_procedimento) and needs_execution(_contributi_tecnici):

            chiudi_azione(_contributi_tecnici)

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.formazione_del_piano,
                    qualifica_richiesta=QualificaRichiesta.COMUNE,
                    stato=STATO_AZIONE.necessaria
                ))

            if procedura_avvio.conferenza_copianificazione == TipologiaCopianificazione.NECESSARIA:

                procedura_avvio.notifica_genio_civile = False
                procedura_avvio.save()

                _cc, created = ConferenzaCopianificazione.objects.get_or_create(piano=piano)
                _cc.data_richiesta_conferenza = datetime.datetime.now(timezone.get_current_timezone())
                _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
                _cc.save()

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.richiesta_integrazioni,
                        qualifica_richiesta=QualificaRichiesta.REGIONE,
                        stato=STATO_AZIONE.attesa
                    ))

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.esito_conferenza_copianificazione,
                        qualifica_richiesta=QualificaRichiesta.REGIONE,
                        stato=STATO_AZIONE.attesa
                    ))

                return "conferenza_copianificazione"

            elif procedura_avvio.conferenza_copianificazione == TipologiaCopianificazione.POSTICIPATA:

                procedura_avvio.notifica_genio_civile = False
                procedura_avvio.save()

                _cc, created = ConferenzaCopianificazione.objects.get_or_create(piano=piano)
                _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
                _cc.save()

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.richiesta_conferenza_copianificazione,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=STATO_AZIONE.attesa
                    ))

                return None

            elif procedura_avvio.conferenza_copianificazione == TipologiaCopianificazione.NON_NECESSARIA:

                procedura_avvio.notifica_genio_civile = True
                procedura_avvio.save()

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.protocollo_genio_civile,
                        qualifica_richiesta=QualificaRichiesta.GC,
                        stato=STATO_AZIONE.necessaria
                    ))

                return "protocollo_genio_civile"

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.PIAN):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            _res = cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            if _res:
                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type=_res)

            return ContributiTecnici(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class RichiestaIntegrazioni(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TipologiaAzione.richiesta_integrazioni

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _richiesta_integrazioni = piano.getFirstAction(TipologiaAzione.richiesta_integrazioni)
        if needs_execution(_richiesta_integrazioni):

            chiudi_azione(_richiesta_integrazioni)

            if procedura_avvio.richiesta_integrazioni:
                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.integrazioni_richieste,
                        qualifica_richiesta=QualificaRichiesta.COMUNE,
                        stato=STATO_AZIONE.attesa
                    ))
            else:
                try_and_close_avvio(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="richiesta_integrazioni")

            check_and_promote(_piano, info)

            return RichiestaIntegrazioni(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class IntegrazioniRichieste(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TipologiaAzione.integrazioni_richieste

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano:Piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA)

        _integrazioni_richieste = piano.getFirstAction(TipologiaAzione.integrazioni_richieste)
        if needs_execution(_integrazioni_richieste):
            chiudi_azione(_integrazioni_richieste)

            try_and_close_avvio(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="integrazioni_richieste")

            check_and_promote(_piano, info)

            return IntegrazioniRichieste(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class InvioProtocolloGenioCivile(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        ensure_fase(fase, Fase.ANAGRAFICA)

        _protocollo_genio_civile = piano.getFirstAction(TipologiaAzione.protocollo_genio_civile)
        if needs_execution(_protocollo_genio_civile):
            now = datetime.datetime.now(timezone.get_current_timezone())
            chiudi_azione(_protocollo_genio_civile, data=now)

            piano.data_protocollo_genio_civile = now
            piano.save()

            return try_and_close_avvio(piano)

        return False

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.GC):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        # check risorsa
        if not _piano.risorse\
                .filter(tipo=TipoRisorsa.DOCUMENTO_GENIO_CIVILE.value, archiviata=False, user=info.context.user)\
                .exists():
            return GraphQLError("Risorsa mancante: {}".format(TipoRisorsa.DOCUMENTO_GENIO_CIVILE.value), code=409)

        try:
            closed = cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            if closed:
                check_and_promote(_piano, info)

            return InvioProtocolloGenioCivile(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class RichiestaConferenzaCopianificazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TipologiaAzione.richiesta_conferenza_copianificazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        ensure_fase(fase, Fase.ANAGRAFICA)

        # _avvio_procedimento = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_procedimento)
        # if isExecuted(_avvio_procedimento):
        if procedura_avvio.conferenza_copianificazione != TipologiaCopianificazione.POSTICIPATA:
            return GraphQLError("Errore nello stato del piano - Tipologia copianificazione errata", code=400)

        _richiesta_cc = piano.getFirstAction(TipologiaAzione.richiesta_conferenza_copianificazione)
        if needs_execution(_richiesta_cc):
            chiudi_azione(_richiesta_cc, set_data=False)

            procedura_avvio.notifica_genio_civile = False
            procedura_avvio.save()

            _cc = ConferenzaCopianificazione.objects.get(piano=piano)
            _cc.data_richiesta_conferenza = get_now()
            _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
            _cc.save()

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.richiesta_integrazioni,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=STATO_AZIONE.attesa
                ))

            crea_azione(
                Azione(
                    piano=piano,
                    tipologia=TipologiaAzione.esito_conferenza_copianificazione,
                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                    stato=STATO_AZIONE.attesa,
                ).imposta_scadenza((
                    get_now(),
                    procedura_avvio.data_scadenza_risposta
                ))
            )

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="conferenza_copianificazione")

            return RichiestaConferenzaCopianificazione(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class ChiusuraConferenzaCopianificazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TipologiaAzione.esito_conferenza_copianificazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_procedimento = piano.getFirstAction(TipologiaAzione.avvio_procedimento)
        if is_executed(_avvio_procedimento):

            _esito_cc = piano.getFirstAction(TipologiaAzione.esito_conferenza_copianificazione)
            if needs_execution(_esito_cc):

                chiudi_azione(_esito_cc, set_data=False)

                procedura_avvio.notifica_genio_civile = True
                procedura_avvio.save()

                now = get_now()

                _cc = ConferenzaCopianificazione.objects.get(piano=piano)
                _cc.data_chiusura_conferenza = now
                _cc.save()

                crea_azione(
                    Azione(
                        piano=piano,
                        tipologia=TipologiaAzione.protocollo_genio_civile,
                        qualifica_richiesta=QualificaRichiesta.GC,
                        stato=STATO_AZIONE.necessaria,
                    ).imposta_scadenza((
                        now,  # ??
                        procedura_avvio.data_scadenza_risposta
                    ))
                )

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        if not auth.can_edit_piano(info.context.user, _piano, QualificaRichiesta.REGIONE):
            return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

        try:
            cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

            # Notify Users
            piano_phase_changed.send(
                sender=Piano,
                user=info.context.user,
                piano=_piano,
                message_type="protocollo_genio_civile")

            check_and_promote(_piano, info)

            return ChiusuraConferenzaCopianificazione(
                avvio_aggiornato=_procedura_avvio,
                errors=[]
            )
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)
