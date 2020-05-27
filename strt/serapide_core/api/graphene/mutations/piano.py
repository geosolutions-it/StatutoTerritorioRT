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

import traceback

import graphene
from graphene import relay
from graphql_extensions.exceptions import GraphQLError

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from serapide_core.api.auth.user import get_assegnamenti, can_admin_delega
from serapide_core.api.piano_utils import (
    needs_execution,
    is_executed,
    ensure_fase,
    chiudi_azione,
    crea_azione,
    chiudi_pendenti, get_now,
)

from strt_users.enums import Profilo
from strt_users.models import (
    Ente, Ufficio,
    Qualifica,
    QualificaUfficio, ProfiloUtente, Token)

from serapide_core.helpers import (
    update_create_instance,
)

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Piano,
    Azione,
    SoggettoOperante,
    Delega,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    PianoControdedotto,
    PianoRevPostCP,

)

from serapide_core.modello.enums import (
    Fase,
    AZIONI_BASE,
    STATO_AZIONE,
    TipologiaVAS,
    TipologiaAzione,
    TipologiaPiano,
)

from serapide_core.api.graphene import (
    types, inputs
)

import serapide_core.api.auth.user as auth
import serapide_core.api.auth.piano as auth_piano

logger = logging.getLogger(__name__)


# ############################################################################ #
# Management Passaggio di Stato Piano
# ############################################################################ #

# def check_and_close_avvio(piano):
#     _conferenza_copianificazione_attiva = \
#         needsExecution(
#             piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione)) or \
#         needsExecution(
#             piano.getFirstAction(TIPOLOGIA_AZIONE.esito_conferenza_copianificazione))
#
#     _protocollo_genio_civile = piano.getFirstAction(TIPOLOGIA_AZIONE.protocollo_genio_civile)
#     _integrazioni_richieste = piano.getFirstAction(TIPOLOGIA_AZIONE.integrazioni_richieste)
#
#     if not _conferenza_copianificazione_attiva and \
#             isExecuted(_protocollo_genio_civile) and \
#             isExecuted(_integrazioni_richieste):
#
#         procedura_vas = ProceduraVAS.objects.get(piano=piano)
#         if procedura_vas.conclusa:
#             piano.chiudi_pendenti(attesa=True, necessaria=False)
#
#         procedura_avvio, _ = ProceduraAvvio.objects.get_or_create(piano=piano)
#         procedura_avvio.conclusa = True
#         procedura_avvio.save()
#
#         ensure_avvio_objects(piano)


# def ensure_avvio_objects(piano):
#     PianoControdedotto.objects.get_or_create(piano=piano)
#     PianoRevPostCP.objects.get_or_create(piano=piano)
#
#     procedura_adozione, _ = ProceduraAdozione.objects.get_or_create(piano=piano, ente=piano.ente)
#     piano.procedura_adozione = procedura_adozione
#     piano.save()


def check_and_promote(piano:Piano, info):
    logger.warning('Check promozione per piano [{c}]:"{d}"  '.format(c=piano.codice,d=piano.descrizione))

    eligible, errs = auth_piano.is_eligible_for_promotion(piano)
    if eligible:
        logger.warning('Promozione Piano [{c}]:"{d}"'.format(c=piano.codice, d=piano.descrizione))

        # if piano.fase == Fase.ANAGRAFICA:
        #     ensure_avvio_objects(piano)

        piano.fase = _fase = piano.fase.getNext()
        piano.save()

        logger.warning("PIANO PROMOSSO {}".format(piano))

        # Notify Users
        piano_phase_changed.send(
            sender=Piano,
            user=info.context.user,
            piano=piano,
            message_type="piano_phase_changed")

        promuovi_piano(_fase, piano)
        return True, []
    else:
        logger.warning('Piano [{c}]:"{d}" non promosso'.format(c=piano.codice, d=piano.descrizione))
        for err in errs:
            logger.warning('  -> {}'.format(err))

    return False, errs


def promuovi_piano(fase:Fase, piano):

    procedura_vas = piano.procedura_vas

    # Update Azioni Piano
    _order = Azione.count_by_piano(piano)

    # - Attach Actions Templates for the Next "Fase"
    for _a in AZIONI_BASE[fase]:
        crea_azione(
            Azione(
                piano=piano,
                tipologia=_a["tipologia"],
                qualifica_richiesta=_a["qualifica"],
                order=_order,
                stato=STATO_AZIONE.necessaria
            ))
        _order += 1

    # - Update Action state accordingly
    if fase == Fase.ANAGRAFICA:
        _creato = piano.getFirstAction(TipologiaAzione.creato_piano)
        if _creato.stato != STATO_AZIONE.necessaria:
            raise Exception("Stato Inconsistente!")

        chiudi_azione(_creato)

    elif fase == Fase.AVVIO:
        ## TODO check -- WTF?????
        _richiesta_integrazioni = piano.getFirstAction(TipologiaAzione.richiesta_integrazioni)
        if needs_execution(_richiesta_integrazioni):
            chiudi_azione(_richiesta_integrazioni)

        _integrazioni_richieste = piano.getFirstAction(TipologiaAzione.integrazioni_richieste)
        if needs_execution(_integrazioni_richieste):
            chiudi_azione(_integrazioni_richieste)


# ############################################################################ #
# MUTATIONS
# ############################################################################ #
class CreatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(inputs.PianoCreateInput)

    nuovo_piano = graphene.Field(types.PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _piano_data = input.get('piano_operativo')
            # Ente (M)
            _data = _piano_data.pop('ente')
            _ente = Ente.objects.get(ipa=_data['ipa'])
            # _role = info.context.session.get('role', None)
            # _token = info.context.session.get('token', None)
            _piano_data['ente'] = _ente

            if not info.context.user:
                return GraphQLError("Unauthorized", code=401)

            if not _ente.is_comune():
                return GraphQLError("Ente deve essere un comune", code=400)

            if not auth.can_create_piano(info.context.user, _ente):
                return GraphQLError("Forbidden: user can't create piano", code=403)

            # create Piano and assign id
            _piano = Piano()
            _piano.ente = _ente  # mandatory field
            _piano.codice = "temp"  # mandatory field
            _piano.save()

            # Codice (M)
            if 'codice' in _piano_data:
                _codice = _piano_data.pop('codice')
            else:
                _year = str(datetime.date.today().year)[2:]
                _month = datetime.date.today().month
                _codice = '%s%02d%02d%05d' % (_ente.ipa, int(_year), _month, _piano.id)

            _piano_data['codice'] = _codice

            # Fase (O)

            _fase = None
            if 'fase' in _piano_data:
                _data = _piano_data.pop('fase')
                _fase = Fase.fix_enum(_data, none_on_error=True)

            _fase = _fase if _fase else Fase.DRAFT
            _piano_data['fase'] = _fase

            # Descrizione (O)
            if 'descrizione' in _piano_data:
                _data = _piano_data.pop('descrizione')
                _piano_data['descrizione'] = _data[0]

            if 'tipologia' in _piano_data:
                _tipologia = _piano_data.pop('tipologia')
                _tipologia = TipologiaPiano.fix_enum(_tipologia, none_on_error=True)
                _piano_data['tipologia'] = _tipologia

            _piano_data['responsabile'] = info.context.user

            # Crea piano
            # _piano = Piano()

            nuovo_piano = update_create_instance(_piano, _piano_data)

            # Inizializzazione Azioni del Piano
            _order = 0

            for _a in AZIONI_BASE[_fase]:
                crea_azione(
                    Azione(
                        piano=nuovo_piano,
                        tipologia=_a["tipologia"],
                        qualifica_richiesta=_a["qualifica"],
                        stato=_a.get('stato', None),
                        order=_order
                    ))
                _order += 1

            # Inizializzazione Procedura VAS
            _procedura_vas, created = ProceduraVAS.objects.get_or_create(
                piano=nuovo_piano,
                tipologia=TipologiaVAS.UNKNOWN)

            # Inizializzazione Procedura Avvio
            _procedura_avvio, created = ProceduraAvvio.objects.get_or_create(piano=nuovo_piano)

            nuovo_piano.procedura_vas = _procedura_vas
            nuovo_piano.procedura_avvio = _procedura_avvio
            nuovo_piano.save()

            return cls(nuovo_piano=nuovo_piano)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UpdatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(inputs.PianoUpdateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    @staticmethod
    def make_token_expiration(days=365):
        _expire_days = getattr(settings, 'TOKEN_EXPIRE_DAYS', days)
        _expire_time = get_now()
        _expire_delta = datetime.timedelta(days=_expire_days)
        return _expire_time + _expire_delta

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice'])
        _piano_input = input.get('piano_operativo')
        _ente = _piano.ente

        if not info.context.user:
            return GraphQLError("Unauthorized", code=401)

        # Primo chek generico di autorizzazione
        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        try:

            for fixed_field in ['codice', 'data_creazione', 'data_accettazione', 'data_avvio',
                                'data_approvazione', 'ente', 'fase', 'tipologia', 'data_protocollo_genio_civile',
                                'responsabile']:
                if fixed_field in _piano_input:
                    logger.warning('Il campo "{}" non può essere modificato attraverso questa operazione'.format(fixed_field))
                    _piano_input.pop(fixed_field)

                # TODO: check what to do with 'data_delibera'

            # ############################################################ #
            # Editable fields - consistency checks
            # ############################################################ #
            # Descrizione (O)
            if 'descrizione' in _piano_input:
                _data = _piano_input.pop('descrizione')
                # if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                _piano.descrizione = _data[0]

            # Data Delibera (O)
            # if 'data_delibera' in _piano_input:
            #     if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            #         _piano_input.pop('data_delibera')
                    # This cannot be changed

            # Soggetto Proponente (O)
            if 'soggetto_proponente_uuid' in _piano_input:

                if not auth.can_edit_piano(info.context.user, _piano, Qualifica.OPCOM):
                    return GraphQLError("Forbidden - Utente non abilitato per questa azione", code=403)

                _soggetto_proponente_uuid = _piano_input.pop('soggetto_proponente_uuid')
                if _soggetto_proponente_uuid:
                    ufficio = Ufficio.objects.filter(uuid=_soggetto_proponente_uuid).get()
                    if not ufficio:
                        return GraphQLError(_("Not found - Ufficio proponente sconosciuto"), code=404)

                    qu = QualificaUfficio.objects.filter(ufficio=ufficio, qualifica=Qualifica.OPCOM).get()
                    if not qu:
                        return GraphQLError(_("Not found - L'ufficio proponente non è responsabile di Comune"), code=404)

                    _piano.soggetto_proponente = qu

                else:
                    _piano.soggetto_proponente = None

            if 'soggetti_operanti' in _piano_input:

                # if not auth.is_soggetto(info.context.user, _piano):
                #     return GraphQLError(_("Forbidden - L'utente non è soggetto"), code=403)

                _soggetti_operanti = _piano_input.pop('soggetti_operanti') # potrebbe essere vuoto

                old_so_qs = SoggettoOperante.objects.filter(piano=_piano)
                old_so_dict = {so.qualifica_ufficio.ufficio.uuid.__str__() + "_" + so.qualifica_ufficio.qualifica.name: so
                               for so in old_so_qs}
                add_so = []

                for _so in _soggetti_operanti:
                    uff = Ufficio.objects.filter(uuid=_so.ufficio_uuid).get()
                    qualifica = Qualifica.fix_enum(_so.qualifica, none_on_error=True)         # TODO: 404
                    hash = _so.ufficio_uuid + "_" + qualifica.name
                    if hash in old_so_dict:
                        del old_so_dict[hash]
                    else:
                        qu = QualificaUfficio.objects \
                            .filter(ufficio=uff, qualifica=qualifica).get()
                        new_so = SoggettoOperante(qualifica_ufficio=qu, piano=_piano)
                        add_so.append(new_so)

                # pre-check
                # - OPCOM può modificare SO con qualunque qualifica
                # - AC può modificare SO con qualifica SCA
                for so in list(old_so_dict.values()) + add_so:
                    if not auth.has_qualifica(info.context.user, _ente, Qualifica.OPCOM):
                        if so.qualifica_ufficio.qualifica == Qualifica.SCA:
                            if not auth.has_qualifica(info.context.user, _ente, Qualifica.AC):
                                return GraphQLError("Utente non abilitato alla modifica di questo SoggettoOperante",
                                                    code=403)

                # remove all SO left in the old_so_dict since they are not in the input list
                for so in old_so_dict.values():
                    for d in Delega.objects.filter(delegante=so):
                        d.token.delete()
                        d.delete()
                    so.delete()

                # create new SO
                for so in add_so:
                    so.save()

            piano_aggiornato = update_create_instance(_piano, _piano_input)
            return cls(piano_aggiornato=piano_aggiornato)

        except (Ufficio.DoesNotExist, QualificaUfficio.DoesNotExist) as e:
            return GraphQLError(e, code=404)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeletePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    success = graphene.Boolean()
    codice_piano = graphene.String()

    def mutate(self, info, **input):
        if not ProfiloUtente.objects\
                .filter(utente=info.context.user, profilo=Profilo.ADMIN_ENTE)\
                .exists():
            return GraphQLError("Utente non abilitato alle eliminazioni di piano", code=403)

        # Fetching input arguments
        _id = input['codice_piano']
        try:
            _piano = Piano.objects.get(codice=_id)
            if ProfiloUtente.objects\
                    .filter(utente=info.context.user, profilo=Profilo.ADMIN_ENTE, ente=_piano.ente)\
                    .exists():
                logger.warning("Eliminazione Piano {}".format(_piano))
                _piano.delete()
                return DeletePiano(success=True, codice_piano=_id)
            else:
                return GraphQLError("Utente non abilitato in questo ente", code=403)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class PromozionePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])

        # Primo chek generico di autorizzazione
        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        try:
            promoted, errors = check_and_promote(_piano, info)

            if promoted:
                return PromozionePiano(
                    piano_aggiornato=_piano,
                    errors=[]
                )
            else:
                return GraphQLError("Dati non corretti", code=409, errors=errors)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class CreaDelega(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)
        # ufficio_uuid = graphene.String(required=True)
        qualifica = graphene.String(required=True)
        mail = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    token = graphene.String()

    @classmethod
    def mutate(cls, root, info, **input):
        def _get_or_create_resp_so():
            so = auth.get_so(info.context.user, _piano, Qualifica.OPCOM).first()

            if not so:
                # l'utente non ha SO direttamente associato, quindi lo creiamo
                ass = get_assegnamenti(info.context.user, _piano.ente, Qualifica.OPCOM).first()
                so = SoggettoOperante(piano=_piano, qualifica_ufficio=ass.qualifica_ufficio)
                so.save()
            return so

        _piano = Piano.objects.get(codice=input['codice_piano'])

        # Primo check generico di autorizzazione
        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        try:
            qualifica = Qualifica.fix_enum(input['qualifica'], none_on_error=True)
            is_resp = auth.has_qualifica(info.context.user, _piano.ente, Qualifica.OPCOM)

            if not qualifica:
                return GraphQLError("Qualifica sconosciuta", code=404)

            elif qualifica == Qualifica.OPCOM:
                return GraphQLError("Qualifica non delegabile", code=400)

            elif qualifica == Qualifica.READONLY:
                # associa alla delega un qualiasi SO associato all'utente
                so = auth.get_so(info.context.user, _piano).first()
                if not so:
                    if is_resp:
                        # l'utente è RESP per l'ente, ma non ha SO direttamente associato, quindi lo creiamo
                        so = _get_or_create_resp_so()
                    else:
                        return GraphQLError("Forbidden - Utente non assegnatario", code=403)
            else:
                #
                so = auth.get_so(info.context.user, _piano, qualifica).first()
                if not so:
                    if is_resp:
                        # l'utente è RESP per l'ente, ma non ha SO direttamente associato, quindi lo creiamo
                        so = _get_or_create_resp_so()
                    else:
                        return GraphQLError("Forbidden - Qualifica non assegnabile", code=403)

            token = Token()
            token.key = Token.generate_key()
            token.expires = datetime.datetime.now() + datetime.timedelta(days=30)  # TODO
            token.save()

            delega = Delega()
            delega.qualifica = qualifica
            delega.delegante = so
            delega.created_by = info.context.user
            delega.token = token
            delega.save()

            # TODO: USE EMAIL
            # piano_phase_changed.send(
            #     sender=Piano,
            #     user=info.context.user,
            #     piano=_piano,
            #     message_type="delega")

            return CreaDelega(
                token = token.key,
                errors=[]
            )

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteDelega(graphene.Mutation):

    class Arguments:
        token = graphene.String()

    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **input):

        try:
            key = input['token']
            token: Token = Token.objects.get(key=key)
            delega: Delega = Delega.objects.get(token=token)
            piano = delega.delegante.piano

            if not auth.can_access_piano(info.context.user, piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            if not can_admin_delega(info.context.user, delega):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questa delega", code=403)

            delega.token.delete()
            delega.delete()

            return DeleteDelega(
                errors=[]
            )

        except (Token.DoesNotExist, Delega.DoesNotExist) as e:
            return GraphQLError(e, code=404)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


def try_and_close_avvio(piano:Piano):

    procedura_avvio: ProceduraAvvio = piano.procedura_avvio
    procedura_vas: ProceduraVAS = piano.procedura_vas

    _conferenza_copianificazione_attiva = \
        needs_execution(piano.getFirstAction(TipologiaAzione.richiesta_conferenza_copianificazione)) or \
        needs_execution(piano.getFirstAction(TipologiaAzione.esito_conferenza_copianificazione))

    _richiesta_integrazioni = piano.getFirstAction(TipologiaAzione.richiesta_integrazioni)
    _integrazioni_richieste = piano.getFirstAction(TipologiaAzione.integrazioni_richieste)

    _protocollo_genio_civile = piano.getFirstAction(TipologiaAzione.protocollo_genio_civile)

    _formazione_del_piano = piano.getFirstAction(TipologiaAzione.formazione_del_piano)

    if not _conferenza_copianificazione_attiva and \
            is_executed(_protocollo_genio_civile) and \
            is_executed(_formazione_del_piano) and \
            (not procedura_avvio.richiesta_integrazioni or (is_executed(_integrazioni_richieste))) and \
            (not procedura_vas or procedura_vas.conclusa or procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA):

        if procedura_vas and procedura_vas.conclusa:
            chiudi_pendenti(piano, attesa=True, necessaria=False)

        procedura_avvio.conclusa = True
        procedura_avvio.save()

        PianoControdedotto.objects.get_or_create(piano=piano)
        PianoRevPostCP.objects.get_or_create(piano=piano)

        procedura_adozione, created = ProceduraAdozione.objects.get_or_create(
            piano=piano)
        piano.procedura_adozione = procedura_adozione
        piano.save()

        return True

    return False
