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
    Ente,
    Qualifica,
)

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

        if not auth.can_edit_piano(info.context.user, _ente):
            if not auth.has_qualifica(info.context.user, _ente, Qualifica.RESP):
                return GraphQLError("Forbidden - L'utente non può editare piani in questo Ente", code=403)

        # if info.context.user and \
        #     rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        #     rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):

        try:

            for fixed_field in ['codice', 'data_creazione', 'data_accettazione', 'data_avvio',
                                'data_approvazione', 'ente', 'fase', 'tipologia', 'data_delibera']:
                if fixed_field in _piano_input:
                    logger.warning('Il campo "{}" non può essere modificato attraverso questa operazione'.format(fixed_field))
                    _piano_input.pop(fixed_field)

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
                _soggetto_proponente_uuid = _piano_input.pop('soggetto_proponente_uuid')
                if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or
                                                              (info.context.user, _role) or
                                                              (info.context.user, _ente), 'Comune'):
                    update_referenti(_piano, Referente.TIPO_PROPONENTE)

                    # if _piano.soggetto_proponente:
                    #     UpdatePiano.delete_token(_piano.soggetto_proponente.user, _piano)
                    #     _piano.soggetto_proponente = None
                    #
                    # if _soggetto_proponente_uuid and len(_soggetto_proponente_uuid) > 0:
                    #     _soggetto_proponente = Contatto.objects.get(uuid=_soggetto_proponente_uuid)
                    #     _new_role = UpdatePiano.get_role(_soggetto_proponente, TIPOLOGIA_ATTORE.unknown)
                    #     UpdatePiano.get_or_create_token(_soggetto_proponente.user, _piano, _new_role)
                    #     _piano.soggetto_proponente = _soggetto_proponente
                else:
                    return GraphQLError(_("Forbidden"), code=403)

            # Autorita' Competente VAS (O)
            if 'autorita_competente_vas' in _piano_input:
                _autorita_competente_vas = _piano_input.pop('autorita_competente_vas')
                if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or \
                                                              (info.context.user, _role) or \
                                                              (info.context.user, _ente), 'Comune'):

                    _piano.autorita_competente_vas.clear()

                    if _autorita_competente_vas:
                        for _ac in _piano.autorita_competente_vas.all():
                            UpdatePiano.delete_token(_ac.user, _piano)

                        if len(_autorita_competente_vas) > 0:

                            _autorita_competenti = []

                            for _contatto_uuid in _autorita_competente_vas:
                                _autorita_competenti.append(AutoritaCompetenteVAS(
                                    piano=_piano,
                                    autorita_competente=Contatto.objects.get(uuid=_contatto_uuid))
                                )

                            for _ac in _autorita_competenti:
                                _new_role = UpdatePiano.get_role(_ac.autorita_competente, TIPOLOGIA_ATTORE.ac)
                                UpdatePiano.get_or_create_token(_ac.autorita_competente.user, _piano, _new_role)
                                _ac.save()
                else:
                    return GraphQLError(_("Forbidden"), code=403)

            # Soggetti SCA (O)
            if 'soggetti_sca' in _piano_input:
                _soggetti_sca_uuid = _piano_input.pop('soggetti_sca')
                if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or \
                                                              (info.context.user, _role) or \
                                                              (info.context.user, _ente), 'Comune'):

                    _piano.soggetti_sca.clear()

                    if _soggetti_sca_uuid:
                        for _sca in _piano.soggetti_sca.all():
                            UpdatePiano.delete_token(_sca.user, _piano)

                        if len(_soggetti_sca_uuid) > 0:

                            _soggetti_sca = []

                            for _contatto_uuid in _soggetti_sca_uuid:
                                _soggetti_sca.append(SoggettiSCA(
                                    piano=_piano,
                                    soggetto_sca=Contatto.objects.get(uuid=_contatto_uuid))
                                )

                            for _sca in _soggetti_sca:
                                _new_role = UpdatePiano.get_role(_sca.soggetto_sca, TIPOLOGIA_ATTORE.sca)
                                UpdatePiano.get_or_create_token(_sca.soggetto_sca.user, _piano, _new_role)
                                _sca.save()
                else:
                    return GraphQLError(_("Forbidden"), code=403)

            # Autorita' Istituzionali (O)
            if 'autorita_istituzionali' in _piano_input:
                _autorita_istituzionali = _piano_input.pop('autorita_istituzionali')
                if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):

                    _piano.autorita_istituzionali.clear()

                    if _autorita_istituzionali:

                        for _ac in _piano.autorita_istituzionali.all():
                            UpdatePiano.delete_token(_ac.user, _piano)

                        if len(_autorita_istituzionali) > 0:

                            _autorita_competenti = []

                            for _contatto_uuid in _autorita_istituzionali:
                                _autorita_competenti.append(AutoritaIstituzionali(
                                    piano=_piano,
                                    autorita_istituzionale=Contatto.objects.get(uuid=_contatto_uuid))
                                )

                            for _ac in _autorita_competenti:
                                _tipologia = TIPOLOGIA_ATTORE.unknown
                                if _ac.autorita_istituzionale.tipologia == TIPOLOGIA_CONTATTO.genio_civile:
                                    _tipologia = TIPOLOGIA_ATTORE.genio_civile
                                elif _ac.autorita_istituzionale.tipologia == TIPOLOGIA_CONTATTO.acvas:
                                    _tipologia = TIPOLOGIA_ATTORE.ac
                                elif _ac.autorita_istituzionale.tipologia == TIPOLOGIA_CONTATTO.sca:
                                    _tipologia = TIPOLOGIA_ATTORE.sca
                                elif _ac.autorita_istituzionale.tipologia == TIPOLOGIA_CONTATTO.ente:
                                    _tipologia = TIPOLOGIA_ATTORE.enti
                                _new_role = UpdatePiano.get_role(_ac.autorita_istituzionale, _tipologia)
                                UpdatePiano.get_or_create_token(_ac.autorita_istituzionale.user, _piano, _new_role)
                                _ac.save()

            # Altri Destinatari (O)
            if 'altri_destinatari' in _piano_input:
                _altri_destinatari = _piano_input.pop('altri_destinatari')
                if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):

                    _piano.altri_destinatari.clear()

                    if _altri_destinatari:
                        for _ac in _piano.altri_destinatari.all():
                            UpdatePiano.delete_token(_ac.user, _piano)

                        if len(_altri_destinatari) > 0:

                            _autorita_competenti = []

                            for _contatto_uuid in _altri_destinatari:
                                _autorita_competenti.append(AltriDestinatari(
                                    piano=_piano,
                                    altro_destinatario=Contatto.objects.get(uuid=_contatto_uuid))
                                )

                            for _ac in _autorita_competenti:
                                _tipologia = TIPOLOGIA_ATTORE.unknown
                                if _ac.altro_destinatario.tipologia == TIPOLOGIA_CONTATTO.genio_civile:
                                    _tipologia = TIPOLOGIA_ATTORE.genio_civile
                                elif _ac.altro_destinatario.tipologia == TIPOLOGIA_CONTATTO.acvas:
                                    _tipologia = TIPOLOGIA_ATTORE.ac
                                elif _ac.altro_destinatario.tipologia == TIPOLOGIA_CONTATTO.sca:
                                    _tipologia = TIPOLOGIA_ATTORE.sca
                                elif _ac.altro_destinatario.tipologia == TIPOLOGIA_CONTATTO.ente:
                                    _tipologia = TIPOLOGIA_ATTORE.enti
                                _new_role = UpdatePiano.get_role(_ac.altro_destinatario, _tipologia)
                                UpdatePiano.get_or_create_token(_ac.altro_destinatario.user, _piano, _new_role)
                                _ac.save()

            # Protocollo Genio Civile
            if 'data_protocollo_genio_civile' in _piano_input:
                _piano_input.pop('data_protocollo_genio_civile')
                # This cannot be changed

            if 'numero_protocollo_genio_civile' in _piano_input:
                if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) or \
                    not rules.test_rule('strt_core.api.is_actor', _token or \
                                                                  (info.context.user, _role) or \
                                                                  (info.context.user, _ente), 'genio_civile'):
                    _piano_input.pop('numero_protocollo_genio_civile')
                    # This can be changed only by Genio Civile

            piano_aggiornato = update_create_instance(_piano, _piano_input)
            return cls(piano_aggiornato=piano_aggiornato)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)
        # else:
        #     return GraphQLError(_("Forbidden"), code=403)


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
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
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

                    return PromozionePiano(
                        piano_aggiornato=_piano,
                        errors=[]
                    )
                else:
                    return GraphQLError(_("Not Allowed"), code=405)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


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
