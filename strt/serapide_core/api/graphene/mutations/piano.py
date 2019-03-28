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
    PianoAuthTokens,
    AutoritaCompetenteVAS,
    AutoritaIstituzionali,
    AltriDestinatari,
    SoggettiSCA,
)

from serapide_core.modello.enums import (
    FASE,
    FASE_NEXT,
    AZIONI_BASE,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
)

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
            _ente = Organization.objects.get(usermembership__member=info.context.user, code=_data['code'])
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

                # Inizializzazione Procedura VAS
                _procedura_vas = ProceduraVAS()
                _procedura_vas.tipologia = TIPOLOGIA_VAS.semplificata

                # Inizializzazione Procedura Avvio
                _procedura_avvio = ProceduraAvvio()

                nuovo_piano = update_create_instance(_piano, _piano_data)

                _procedura_vas.piano = nuovo_piano
                _procedura_vas.ente = nuovo_piano.ente
                _procedura_vas.save()

                _procedura_avvio.piano = nuovo_piano
                _procedura_avvio.ente = nuovo_piano.ente
                _procedura_avvio.save()

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
    def make_token_expiration(days=365):
        _expire_days = getattr(settings, 'TOKEN_EXPIRE_DAYS', days)
        _expire_time = datetime.datetime.now(timezone.get_current_timezone())
        _expire_delta = datetime.timedelta(days=_expire_days)
        return _expire_time + _expire_delta

    @staticmethod
    def get_or_create_token(user, piano):
        _allowed_tokens = Token.objects.filter(user=user)
        _auth_token = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
        if not _auth_token:
            _token_key = Token.generate_key()
            _new_token, created = Token.objects.get_or_create(
                key=_token_key,
                defaults={
                    'user': user,
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
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
                        if _piano.soggetto_proponente:
                            UpdatePiano.delete_token(_piano.soggetto_proponente.user, _piano)
                            _piano.soggetto_proponente = None

                        if _soggetto_proponente_uuid and len(_soggetto_proponente_uuid) > 0:
                            _soggetto_proponente = Contatto.objects.get(uuid=_soggetto_proponente_uuid)
                            UpdatePiano.get_or_create_token(_soggetto_proponente.user, _piano)
                            _piano.soggetto_proponente = _soggetto_proponente
                    else:
                        return GraphQLError(_("Forbidden"), code=403)

                # Autorità Competente VAS (O)
                if 'autorita_competente_vas' in _piano_data:
                    _autorita_competente_vas = _piano_data.pop('autorita_competente_vas')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
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
                                    UpdatePiano.get_or_create_token(_ac.autorita_competente.user, _piano)
                                    _ac.save()
                    else:
                        return GraphQLError(_("Forbidden"), code=403)

                # Soggetti SCA (O)
                if 'soggetti_sca' in _piano_data:
                    _soggetti_sca_uuid = _piano_data.pop('soggetti_sca')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) and \
                    rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
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
                                    UpdatePiano.get_or_create_token(_sca.soggetto_sca.user, _piano)
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
                                    UpdatePiano.get_or_create_token(_ac.autorita_istituzionale.user, _piano)
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
                                    UpdatePiano.get_or_create_token(_ac.altro_destinatario.user, _piano)
                                    _ac.save()

                # Protocollo Genio Civile
                if 'data_protocollo_genio_civile' in _piano_data:
                    _piano_data.pop('data_protocollo_genio_civile')
                    # This cannot be changed

                if 'numero_protocollo_genio_civile' in _piano_data:
                    if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano) or \
                    not rules.test_rule('strt_core.api.is_actor', _token or
                                        (info.context.user, _organization), 'genio_civile'):
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
    def get_next_phase(cls, fase):
        return FASE_NEXT[fase.nome]

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = 0
        for _a in piano.azioni.all():
            # _a.stato = STATO_AZIONE.nessuna
            _a.data = datetime.datetime.now(timezone.get_current_timezone())
            _a.save()
            _order += 1

        # - Attach Actions Templates for the Next "Fase"
        for _a in AZIONI_BASE[fase.nome]:
            _azione = Azione(
                tipologia=_a["tipologia"],
                attore=_a["attore"],
                order=_order,
                stato=STATO_AZIONE.necessaria
            )
            _azione.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_azione, piano=piano)

        # - Update Action state accordingly
        if fase.nome == FASE.anagrafica:
            _creato = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
            if _creato.stato != STATO_AZIONE.necessaria:
                raise Exception("Stato Inconsistente!")

            if _creato:
                _creato.stato = STATO_AZIONE.nessuna
                _creato.data = datetime.datetime.now(timezone.get_current_timezone())
                _creato.save()

            _verifica_vas = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.richiesta_verifica_vas).first()
            if _verifica_vas:
                if procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                    _verifica_vas.stato = STATO_AZIONE.nessuna

                elif procedura_vas.tipologia in \
                (TIPOLOGIA_VAS.procedimento, TIPOLOGIA_VAS.procedimento_semplificato):
                    _verifica_vas.stato = STATO_AZIONE.nessuna
                    _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
                    _verifica_vas.data = datetime.datetime.now(timezone.get_current_timezone()) + \
                    datetime.timedelta(days=_verifica_vas_expire_days)

                    _avvio_consultazioni_sca_ac_expire_days = 10
                    _avvio_consultazioni_sca = Azione(
                        tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca,
                        attore=TIPOLOGIA_ATTORE.ac,
                        order=_order,
                        stato=STATO_AZIONE.attesa,
                        data=datetime.datetime.now(timezone.get_current_timezone()) +
                        datetime.timedelta(days=_avvio_consultazioni_sca_ac_expire_days)
                    )
                    _avvio_consultazioni_sca.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_avvio_consultazioni_sca, piano=piano)

                elif procedura_vas.tipologia == TIPOLOGIA_VAS.semplificata:
                    _verifica_vas.stato = STATO_AZIONE.nessuna

                    _emissione_provvedimento_verifica_expire_days = 30
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

                elif procedura_vas.tipologia == TIPOLOGIA_VAS.verifica:
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

                _verifica_vas.save()

        elif fase.nome == FASE.avvio:
            _genio_civile = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile).first()
            if _genio_civile:
                _genio_civile.stato = STATO_AZIONE.attesa
                _genio_civile.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas = ProceduraVAS.objects.get(piano=_piano)
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                _next_fase = cls.get_next_phase(_piano.fase)
                if rules.test_rule('strt_core.api.fase_{next}_completa'.format(
                                   next=_next_fase),
                                   _piano,
                                   _procedura_vas):
                    _piano.fase = _fase = Fase.objects.get(nome=_next_fase)

                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="piano_phase_changed")

                    _piano.save()

                    cls.update_actions_for_phase(_fase, _piano, _procedura_vas)

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
