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

from strt_users.models import (
    Ente, Ufficio,
    Qualifica,
    QualificaUfficio)

from serapide_core.helpers import (
    is_RUP,
    update_create_instance,
)

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    SoggettoOperante,
    Delega,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    PianoControdedotto,
    PianoRevPostCP,
    # PianoAuthTokens,

    needsExecution,
    isExecuted,
    crea_azione,
)

from serapide_core.modello.enums import (
    Fase,
    AZIONI_BASE,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
)

from serapide_core.api.graphene import types
from serapide_core.api.graphene import inputs
from serapide_core.api.graphene.mutations import fase

import serapide_core.api.auth.user as auth
import serapide_core.api.auth.piano as auth_piano

logger = logging.getLogger(__name__)


# ############################################################################ #
# Management Passaggio di Stato Piano
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
            _role = info.context.session.get('role', None)
            _token = info.context.session.get('token', None)
            _piano_data['ente'] = _ente

            if not info.context.user:
                return GraphQLError("Unauthorized", code=401)

            if not _ente.is_comune():
                return GraphQLError("Ente deve essere un comune", code=400)

            if not auth.can_create_piano(info.context.user, _ente):
                return GraphQLError("Forbidden: user can't create piano", code=403)

            #     and \
            # rules.test_rule('strt_users.is_RUP_of', info.context.user, _ente) and \
            # rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _ente), 'Comune'):

            # Codice (M)
            if 'codice' in _piano_data:
                _data = _piano_data.pop('codice')
                _codice = _data
            else:
                _year = str(datetime.date.today().year)[2:]
                _month = datetime.date.today().month
                _piano_id = Piano.objects.filter(ente=_ente).count() + 1
                _codice = '%s%02d%02d%05d' % (_ente.ipa, int(_year), _month, _piano_id)
                _cnt = 1
                while Piano.objects.filter(codice=_codice).count() > 0:
                    _cnt += 1
                    _piano_id = Piano.objects.filter(ente=_ente).count() + _cnt
                    _codice = '%s%02d%02d%05d' % (_ente.ipa, int(_year), _month, _piano_id)
            _piano_data['codice'] = _codice

            # Fase (O)
            if 'fase' in _piano_data:
                _data = _piano_data.pop('fase')
                _fase = Fase[_data]
            else:
                _fase = Fase.DRAFT
            _piano_data['fase'] = _fase

            # Descrizione (O)
            if 'descrizione' in _piano_data:
                _data = _piano_data.pop('descrizione')
                _piano_data['descrizione'] = _data[0]
            _piano_data['user'] = info.context.user

            # Crea piano
            _piano = Piano()

            nuovo_piano = update_create_instance(_piano, _piano_data)

            # Inizializzazione Azioni del Piano
            _order = 0

            for _a in AZIONI_BASE[_fase]:
                crea_azione(Azione(
                                piano=nuovo_piano,
                                tipologia=_a["tipologia"],
                                qualifica_richiesta=_a["qualifica"],
                                stato = _a.get('stato', None),
                                order=_order
                            ))
                _order += 1


            # Inizializzazione Procedura VAS
            _procedura_vas, created = ProceduraVAS.objects.get_or_create(
                piano=nuovo_piano,
                ente=nuovo_piano.ente,
                tipologia=TIPOLOGIA_VAS.unknown)

            # Inizializzazione Procedura Avvio
            _procedura_avvio, created = ProceduraAvvio.objects.get_or_create(
                piano=nuovo_piano,
                ente=nuovo_piano.ente)

            nuovo_piano.procedura_vas = _procedura_vas
            nuovo_piano.procedura_avvio = _procedura_avvio
            nuovo_piano.save()

            return cls(nuovo_piano=nuovo_piano)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


def update_referenti(piano, tipo):

    # TODO
    pass
    # referenti = Referente.objects.filter(piano=piano, tipo=tipo)
    # referenti.delete();
    #
    # if _piano.soggetto_proponente:
    #     UpdatePiano.delete_token(_piano.soggetto_proponente.user, _piano)
    #     _piano.soggetto_proponente = None
    #
    # if _soggetto_proponente_uuid and len(_soggetto_proponente_uuid) > 0:
    #     _soggetto_proponente = Contatto.objects.get(uuid=_soggetto_proponente_uuid)
    #     _new_role = UpdatePiano.get_role(_soggetto_proponente, TIPOLOGIA_ATTORE.unknown)
    #     UpdatePiano.get_or_create_token(_soggetto_proponente.user, _piano, _new_role)
    #     _piano.soggetto_proponente = _soggetto_proponente


class UpdatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(inputs.PianoUpdateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    # @staticmethod
    # def get_role(contact, actor):
    #
    #     _new_role = Ruolo.objects.filter(
    #         qualifica=actor,
    #         utente=contact.user,
    #         ente=contact.ente
    #     ).first()
    #
    #     if not _new_role:
    #         _new_role_type, created = Ruolo.objects.get_or_create(
    #             code=settings.TEMP_USER_CODE,
    #             organization_type=contact.ente.type
    #         )
    #
    #         _new_role_name = '%s-%s-%s' % (contact.user.fiscal_code,
    #                                        contact.ente.code,
    #                                        actor)
    #         _new_role, created = Ruolo.objects.get_or_create(
    #             nome=_new_role_name,
    #             qualifica=actor,
    #             description='%s - %s' % (_new_role_type.description, contact.ente.name),
    #             utente=contact.user,
    #             ente=contact.ente,
    #             type=_new_role_type
    #         )
    #     return _new_role

    @staticmethod
    def make_token_expiration(days=365):
        _expire_days = getattr(settings, 'TOKEN_EXPIRE_DAYS', days)
        _expire_time = datetime.datetime.now(timezone.get_current_timezone())
        _expire_delta = datetime.timedelta(days=_expire_days)
        return _expire_time + _expire_delta

    # @staticmethod
    # def get_or_create_token(user, piano, role):
    #     _allowed_tokens = Delega.objects.filter(user=user, membership=role)
    #     _auth_token = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
    #     if not _auth_token:
    #         _token_key = Delega.generate_key()
    #         _new_token, created = Delega.objects.get_or_create(
    #             key=_token_key,
    #             defaults={
    #                 'user': user,
    #                 'membership': role,
    #                 'expires': UpdatePiano.make_token_expiration()
    #             }
    #         )
    #
    #         _auth_token, created = PianoAuthTokens.objects.get_or_create(
    #             piano=piano,
    #             token=_new_token
    #         )
    #
    #         _new_token.save()
    #         _auth_token.save()

    # @staticmethod
    # def delete_token(user, piano):
    #     _allowed_tokens = Delega.objects.filter(user=user)
    #     _auth_tokens = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
    #     for _at in _auth_tokens:
    #         _at.token.delete()
    #     _auth_tokens.delete()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice'])
        _piano_input = input.get('piano_operativo')
        # _role = info.context.session['role'] if 'role' in info.context.session else None
        # _token = info.context.session['token'] if 'token' in info.context.session else None
        _ente = _piano.ente

        if not info.context.user:
            return GraphQLError("Unauthorized", code=401)

        # Primo chek generico di autorizzazione
        if not auth.has_qualifica(info.context.user, _ente, Qualifica.RESP):
            if not auth.is_soggetto(info.context.user, _piano):
                return GraphQLError("Forbidden - Pre-check: L'utente non può editare piani in questo Ente", code=403)

        try:

            for fixed_field in ['codice', 'data_creazione', 'data_accettazione', 'data_avvio',
                                'data_approvazione', 'ente', 'fase', 'tipologia', 'data_protocollo_genio_civile']:
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

                if not auth.has_qualifica(info.context.user, _ente, Qualifica.RESP):
                    return GraphQLError("Forbidden - Richiesta qualifica Responsabile", code=403)

                _soggetto_proponente_uuid = _piano_input.pop('soggetto_proponente_uuid')
                ufficio = Ufficio.objects.filter(uuid=_soggetto_proponente_uuid).get()
                if not ufficio:
                    return GraphQLError(_("Not found - Ufficio proponente sconosciuto"), code=404)

                qu = QualificaUfficio.objects.filter(ufficio=ufficio, qualifica=Qualifica.RESP).get()
                if not qu:
                    return GraphQLError(_("Not found - L'ufficio proponente non è responsabile di Comune"), code=404)

                _piano.soggetto_proponente = qu

            if 'soggetti_operanti' in _piano_input:

                # if not auth.is_soggetto(info.context.user, _piano):
                #     return GraphQLError(_("Forbidden - L'utente non è soggetto"), code=403)

                _soggetti_operanti = _piano_input.pop('soggetti_operanti')
                if _soggetti_operanti:

                    old_so_qs = SoggettoOperante.objects.filter(piano=_piano)
                    old_so_dict = {so.qualifica_ufficio.ufficio.uuid + "_" + so.qualifica_ufficio.qualifica: so
                                   for so in old_so_qs}
                    add_so = []

                    for so in _soggetti_operanti:
                        uff = Ufficio.objects.filter(uuid=so.ufficio_uuid).get() # TODO: 404
                        qualifica = Qualifica[so.qualifica]                      # TODO: 404
                        hash = so.ufficio_uuid + "_" + so.qualifica
                        if hash in old_so_dict:
                            del old_so_dict[hash]
                        else:
                            qu = QualificaUfficio.objects.filter \
                                .filter(ufficio=uff, qualifica=qualifica).get()  # TODO: 404
                            new_so = SoggettoOperante(qualifica_ufficio=qu, piano=_piano)
                            add_so.append(new_so)

                    # pre-check
                    if not auth.has_qualifica(info.context.user, _ente, Qualifica.RESP):
                        for so in old_so_dict.values() + add_so:
                            if so.qualifica_ufficio.qualifica in [Qualifica.AC, Qualifica.SCA]:
                                return GraphQLError("Forbidden - Richiesta qualifica Responsabile", code=403)

                    ## remove all SO left in the old_so_dict since they are not in the input list
                    for so in old_so_dict.values():
                        so.delete()

                    # create new SO
                    for so in add_so:
                        so.save()

            if 'numero_protocollo_genio_civile' in _piano_input:
                if not auth.is_soggetto_operante(info.context.user, _piano, Qualifica.GC):
                    return GraphQLError("Forbidden - Campo modificabile solo dal GC", code=403)
                    # This can be changed only by Genio Civile

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
        if info.context.user and is_RUP(info.context.user):

            # Fetching input arguments
            _id = input['codice_piano']
            try:
                _piano = Piano.objects.get(codice=_id)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                    _piano.delete()

                    return DeletePiano(success=True, codice_piano=_id)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        return DeletePiano(success=False)


class PromozionePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])

        # Primo chek generico di autorizzazione

        # if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
        if not auth.has_qualifica(info.context.user, _piano.ente, Qualifica.RESP):
            if not auth.is_soggetto(info.context.user, _piano):
                return GraphQLError("Forbidden - Pre-check: L'utente non può editare piani in questo Ente", code=403)

        try:
            # def is_eligible_for_promotion(self):
            #     _res = rules.test_rule('strt_core.api.fase_{next}_completa'.format(
            #         next=self.next_phase),
            #         self,
            #         self.procedura_vas)

            eligible, errors = auth_piano.is_eligible_for_promotion(_piano)
            if eligible:
                _piano.fase = _piano.fase.getNext()
                _piano.save()

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="piano_phase_changed")

                fase.promuovi_piano(_piano.fase, _piano)

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


class FormazionePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(types.PianoNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas, user):

        # Update Azioni Piano
        # - Update Action state accordingly
        if fase.nome == FASE.anagrafica:

            _formazione_del_piano = piano.getFirstAction(TIPOLOGIA_AZIONE.formazione_del_piano)
            if needsExecution(_formazione_del_piano):
                _formazione_del_piano.stato = STATO_AZIONE.nessuna
                _formazione_del_piano.data = datetime.datetime.now(timezone.get_current_timezone())
                _formazione_del_piano.save()

                _conferenza_copianificazione_attiva = \
                     needsExecution(
                        piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione)) or \
                    needsExecution(
                        piano.getFirstAction(TIPOLOGIA_AZIONE.esito_conferenza_copianificazione))

                _protocollo_genio_civile = piano.getFirstAction(TIPOLOGIA_AZIONE.protocollo_genio_civile)
                _integrazioni_richieste = piano.getFirstAction(TIPOLOGIA_AZIONE.integrazioni_richieste)

                if not _conferenza_copianificazione_attiva and \
                    isExecuted(_protocollo_genio_civile) and \
                    isExecuted(_integrazioni_richieste):

                    if procedura_vas.conclusa:
                        piano.chiudi_pendenti(attesa=True, necessaria=False)
                    procedura_avvio, created = ProceduraAvvio.objects.get_or_create(piano=piano)
                    procedura_avvio.conclusa = True
                    procedura_avvio.save()

                    procedura_adozione, created = ProceduraAdozione.objects.get_or_create(piano=piano, ente=piano.ente)

                    PianoControdedotto.objects.get_or_create(piano=piano)
                    PianoRevPostCP.objects.get_or_create(piano=piano)

                    piano.procedura_adozione = procedura_adozione
                    piano.save()
        else:
            raise Exception(_("Fase Piano incongruente con l'azione richiesta"))

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas = ProceduraVAS.objects.get(piano=_piano)
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

                return FormazionePiano(
                    piano_aggiornato=_piano,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
