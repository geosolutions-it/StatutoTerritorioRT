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
    Organization,
    Token,
    MembershipType,
    UserMembership,
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
    Contatto,
    AzioniPiano,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    PianoControdedotto,
    PianoRevPostCP,
    PianoAuthTokens,
    AutoritaCompetenteVAS,
    AutoritaIstituzionali,
    AltriDestinatari,
    SoggettiSCA,
)

from serapide_core.modello.enums import (
    FASE,
    AZIONI_BASE,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
)

from . import fase
from .. import types
from .. import inputs

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
            _ente = Organization.objects.get(code=_data['code'])
            _piano_data['ente'] = _ente
            if info.context.user and rules.test_rule('strt_users.is_RUP_of', info.context.user, _ente):

                # Codice (M)
                if 'codice' in _piano_data:
                    _data = _piano_data.pop('codice')
                    _codice = _data
                else:
                    _year = str(datetime.date.today().year)[2:]
                    _month = datetime.date.today().month
                    _piano_id = Piano.objects.filter(ente=_ente).count() + 1
                    _codice = '%s%02d%02d%05d' % (_ente.code, int(_year), _month, _piano_id)
                _piano_data['codice'] = _codice

                # Fase (O)
                if 'fase' in _piano_data:
                    _data = _piano_data.pop('fase')
                    _fase = Fase.objects.get(codice=_data['codice'])
                else:
                    _fase = Fase.objects.get(codice='FP255')
                _piano_data['fase'] = _fase

                # Descrizione (O)
                if 'descrizione' in _piano_data:
                    _data = _piano_data.pop('descrizione')
                    _piano_data['descrizione'] = _data[0]
                _piano_data['user'] = info.context.user
                _piano = Piano()

                # Inizializzazione Azioni del Piano
                _order = 0
                _azioni_piano = []
                for _a in AZIONI_BASE[_fase.nome]:
                    _azione = Azione(
                        tipologia=_a["tipologia"],
                        attore=_a["attore"],
                        order=_order
                    )
                    _azioni_piano.append(_azione)
                    _order += 1

                nuovo_piano = update_create_instance(_piano, _piano_data)

                # Inizializzazione Procedura VAS
                _procedura_vas, created = ProceduraVAS.objects.get_or_create(
                    piano=nuovo_piano,
                    ente=nuovo_piano.ente,
                    tipologia=TIPOLOGIA_VAS.semplificata)

                # Inizializzazione Procedura Avvio
                _procedura_avvio, created = ProceduraAvvio.objects.get_or_create(
                    piano=nuovo_piano,
                    ente=nuovo_piano.ente)

                nuovo_piano.procedura_vas = _procedura_vas
                nuovo_piano.procedura_avvio = _procedura_avvio
                nuovo_piano.save()

                for _ap in _azioni_piano:
                    _ap.save()
                    AzioniPiano.objects.get_or_create(azione=_ap, piano=nuovo_piano)

                _creato = nuovo_piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
                if _creato:
                    _creato.stato = STATO_AZIONE.necessaria
                    _creato.save()

                return cls(nuovo_piano=nuovo_piano)
            else:
                return GraphQLError(_("Forbidden"), code=403)
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
    def get_role(contact, actor):
        _new_role_type, created = MembershipType.objects.get_or_create(
            code=settings.TEMP_USER_CODE,
            organization_type=contact.ente.type
        )
        _new_role_name = '%s-%s-membership' % (contact.user.fiscal_code,
                                               contact.ente.code)
        _new_role, created = UserMembership.objects.get_or_create(
            name=_new_role_name,
            attore=actor,
            description='%s - %s' % (_new_role_type.description, contact.ente.name),
            member=contact.user,
            organization=contact.ente,
            type=_new_role_type
        )
        return _new_role

    @staticmethod
    def make_token_expiration(days=365):
        _expire_days = getattr(settings, 'TOKEN_EXPIRE_DAYS', days)
        _expire_time = datetime.datetime.now(timezone.get_current_timezone())
        _expire_delta = datetime.timedelta(days=_expire_days)
        return _expire_time + _expire_delta

    @staticmethod
    def get_or_create_token(user, piano, role):
        _allowed_tokens = Token.objects.filter(user=user, membership=role)
        _auth_token = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
        if not _auth_token:
            _token_key = Token.generate_key()
            _new_token, created = Token.objects.get_or_create(
                key=_token_key,
                defaults={
                    'user': user,
                    'membership': role,
                    'expires': UpdatePiano.make_token_expiration()
                }
            )

            _auth_token, created = PianoAuthTokens.objects.get_or_create(
                piano=piano,
                token=_new_token
            )

            _new_token.save()
            _auth_token.save()

    @staticmethod
    def delete_token(user, piano):
        _allowed_tokens = Token.objects.filter(user=user)
        _auth_tokens = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
        for _at in _auth_tokens:
            _at.token.delete()
        _auth_tokens.delete()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice'])
        _piano_data = input.get('piano_operativo')
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # Codice Piano (M)
                if 'codice' in _piano_data:
                    _piano_data.pop('codice')
                    # This cannot be changed

                # Data Accettazione (M)
                if 'data_creazione' in _piano_data:
                    _piano_data.pop('data_creazione')
                    # This cannot be changed

                # Data Accettazione (O)
                if 'data_accettazione' in _piano_data:
                    _piano_data.pop('data_accettazione')
                    # This cannot be changed

                # Data Avvio (O)
                if 'data_avvio' in _piano_data:
                    _piano_data.pop('data_avvio')
                    # This cannot be changed

                # Data Approvazione (O)
                if 'data_approvazione' in _piano_data:
                    _piano_data.pop('data_approvazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _piano_data:
                    _piano_data.pop('ente')
                    # This cannot be changed

                # Fase (O)
                if 'fase' in _piano_data:
                    _piano_data.pop('fase')
                    # This cannot be changed

                # Tipologia (O)
                if 'tipologia' in _piano_data:
                    _piano_data.pop('tipologia')
                    # This cannot be changed

                # ############################################################ #
                # Editable fields - consistency checks
                # ############################################################ #
                # Descrizione (O)
                if 'descrizione' in _piano_data:
                    _data = _piano_data.pop('descrizione')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano.descrizione = _data[0]

                # Data Delibera (O)
                if 'data_delibera' in _piano_data:
                    if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano_data.pop('data_delibera')
                        # This cannot be changed

                # Soggetto Proponente (O)
                if 'soggetto_proponente_uuid' in _piano_data:
                    _soggetto_proponente_uuid = _piano_data.pop('soggetto_proponente_uuid')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):

                        if _piano.soggetto_proponente:
                            UpdatePiano.delete_token(_piano.soggetto_proponente.user, _piano)
                            _piano.soggetto_proponente = None

                        if _soggetto_proponente_uuid and len(_soggetto_proponente_uuid) > 0:
                            _soggetto_proponente = Contatto.objects.get(uuid=_soggetto_proponente_uuid)
                            _attore = TIPOLOGIA_ATTORE.unknown
                            _new_role = UpdatePiano.get_role(_soggetto_proponente, _attore)
                            UpdatePiano.get_or_create_token(_soggetto_proponente.user, _piano, _new_role)
                            _piano.soggetto_proponente = _soggetto_proponente
                    else:
                        return GraphQLError(_("Forbidden"), code=403)

                # Autorità Competente VAS (O)
                if 'autorita_competente_vas' in _piano_data:
                    _autorita_competente_vas = _piano_data.pop('autorita_competente_vas')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):

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
                if 'soggetti_sca' in _piano_data:
                    _soggetti_sca_uuid = _piano_data.pop('soggetti_sca')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):

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

                # Autorità Istituzionali (O)
                if 'autorita_istituzionali' in _piano_data:
                    _autorita_istituzionali = _piano_data.pop('autorita_istituzionali')
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
                                    _new_role = UpdatePiano.get_role(_ac.autorita_istituzionale, TIPOLOGIA_ATTORE.ac)
                                    UpdatePiano.get_or_create_token(_ac.autorita_istituzionale.user, _piano, _new_role)
                                    _ac.save()

                # Altri Destinatari (O)
                if 'altri_destinatari' in _piano_data:
                    _altri_destinatari = _piano_data.pop('altri_destinatari')
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
                                    _new_role = UpdatePiano.get_role(_ac.altro_destinatario, TIPOLOGIA_ATTORE.ac)
                                    UpdatePiano.get_or_create_token(_ac.altro_destinatario.user, _piano, _new_role)
                                    _ac.save()

                # Protocollo Genio Civile
                if 'data_protocollo_genio_civile' in _piano_data:
                    _piano_data.pop('data_protocollo_genio_civile')
                    # This cannot be changed

                if 'numero_protocollo_genio_civile' in _piano_data:
                    if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) or \
                    not rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'genio_civile'):
                        _piano_data.pop('numero_protocollo_genio_civile')
                        # This can be changed only by Genio Civile

                piano_aggiornato = update_create_instance(_piano, _piano_data)
                return cls(piano_aggiornato=piano_aggiornato)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


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

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    _piano.save()
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
            _formazione_del_piano = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.formazione_del_piano).first()
            if _formazione_del_piano and _formazione_del_piano.stato != STATO_AZIONE.nessuna:
                _formazione_del_piano.stato = STATO_AZIONE.nessuna
                _formazione_del_piano.data = datetime.datetime.now(timezone.get_current_timezone())
                _formazione_del_piano.save()

                _conferenza_copianificazione_attiva = False

                _richiesta_conferenza_copianificazione = piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione).first()
                if _richiesta_conferenza_copianificazione and \
                _richiesta_conferenza_copianificazione.stato != STATO_AZIONE.nessuna:
                    _conferenza_copianificazione_attiva = True

                _esito_conferenza_copianificazione = piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.esito_conferenza_copianificazione).first()
                if _esito_conferenza_copianificazione and \
                _esito_conferenza_copianificazione.stato != STATO_AZIONE.nessuna:
                    _conferenza_copianificazione_attiva = True

                _protocollo_genio_civile = piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile).first()

                _protocollo_genio_civile_id = piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile_id).first()

                _integrazioni_richieste = piano.azioni.filter(
                    tipologia=TIPOLOGIA_AZIONE.integrazioni_richieste).first()

                if not _conferenza_copianificazione_attiva and \
                _protocollo_genio_civile and _protocollo_genio_civile.stato == STATO_AZIONE.nessuna and \
                _protocollo_genio_civile_id and _protocollo_genio_civile_id.stato == STATO_AZIONE.nessuna and \
                _integrazioni_richieste and _integrazioni_richieste.stato == STATO_AZIONE.nessuna:

                    if procedura_vas.conclusa:
                        piano.chiudi_pendenti()
                    procedura_avvio, created = ProceduraAvvio.objects.get_or_create(piano=piano)
                    procedura_avvio.conclusa = True
                    procedura_avvio.save()

                    procedura_adozione, created = ProceduraAdozione.objects.get_or_create(
                        piano=piano, ente=piano.ente)

                    piano_controdedotto, created = PianoControdedotto.objects.get_or_create(piano=piano)
                    piano_rev_post_cp, created = PianoRevPostCP.objects.get_or_create(piano=piano)

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
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_vas, info.context.user)

                if _piano.is_eligible_for_promotion:
                    _piano.fase = _fase = Fase.objects.get(nome=_piano.next_phase)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    _piano.save()
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
