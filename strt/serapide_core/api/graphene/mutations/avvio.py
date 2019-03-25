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

from django.utils import timezone
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
    Piano,
    Azione,
    AzioniPiano,
    ProceduraAvvio,
)

from serapide_core.modello.enums import (
    FASE,
    STATO_AZIONE,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
    TIPOLOGIA_CONF_COPIANIFIZAZIONE,
)

from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateProceduraAvvio(relay.ClientIDMutation):

    class Input:
        procedura_avvio = graphene.Argument(inputs.ProceduraAvvioCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_avvio = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_avvio_data = input.get('procedura_avvio')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraAvvio (M)
                _procedura_avvio_data['piano'] = _piano
                # Ente (M)
                _procedura_avvio_data['ente'] = _piano.ente

                _procedura_avvio = ProceduraAvvio()
                _procedura_avvio.piano = _piano
                _procedura_avvio_data['id'] = _procedura_avvio.id
                _procedura_avvio_data['uuid'] = _procedura_avvio.uuid
                nuova_procedura_avvio = update_create_instance(_procedura_avvio, _procedura_avvio_data)
                return cls(nuova_procedura_avvio=nuova_procedura_avvio)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


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
        if 'piano' in _procedura_avvio_data:
            # This cannot be changed
            _procedura_avvio_data.pop('piano')
        _piano = _procedura_avvio.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _ente = _piano.ente
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('ente')
                    # This cannot be changed

                # Tipologia (O)
                if 'conferenza_copianificazione' in _procedura_avvio_data and \
                (rules.test_rule('strt_users.is_superuser', info.context.user) or is_RUP(info.context.user) or
                 rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _ente), 'Comune')):
                    _conferenza_copianificazione = _procedura_avvio_data.pop('conferenza_copianificazione')
                    if _conferenza_copianificazione and _conferenza_copianificazione in TIPOLOGIA_CONF_COPIANIFIZAZIONE:
                        _procedura_avvio_data['conferenza_copianificazione'] = _conferenza_copianificazione

                procedura_avvio_aggiornata = update_create_instance(_procedura_avvio, _procedura_avvio_data)

                return cls(procedura_avvio_aggiornata=procedura_avvio_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class AvvioPiano(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def autorita_ok(cls, piano):
        _res = False
        _has_genio_civile = False
        if piano.soggetto_proponente and \
        piano.autorita_competente_vas.all().count() > 0 and \
        piano.autorita_istituzionali.all().count() > 0 and \
        piano.altri_destinatari.all().count() > 0 and \
        piano.soggetti_sca.all().count() > 0:
            for _c in piano.soggetti_sca.all():
                if _c.tipologia == TIPOLOGIA_CONTATTO.genio_civile:
                    _has_genio_civile = True
                    break
            for _c in piano.autorita_istituzionali.all():
                if _c.tipologia == TIPOLOGIA_CONTATTO.genio_civile:
                    _has_genio_civile = True
                    break
            for _c in piano.altri_destinatari.all():
                if _c.tipologia == TIPOLOGIA_CONTATTO.genio_civile:
                    _has_genio_civile = True
                    break
            _res = _has_genio_civile
        return _res


    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = 0
        for _a in piano.azioni.all():
            _order += 1

        # - Update Action state accordingly
        if fase.nome == FASE.anagrafica:
            _avvio_procedimento = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.avvio_procedimento).first()
            if _avvio_procedimento and _avvio_procedimento.stato != STATO_AZIONE.nessuna:
                _avvio_procedimento.stato = STATO_AZIONE.nessuna
                _avvio_procedimento.data = datetime.datetime.now(timezone.get_current_timezone())
                _avvio_procedimento.save()

                _formazione_del_piano = Azione(
                    tipologia=TIPOLOGIA_AZIONE.formazione_del_piano,
                    attore=TIPOLOGIA_ATTORE.comune,
                    order=_order,
                    stato=STATO_AZIONE.necessaria
                )
                _formazione_del_piano.save()
                _order += 1
                AzioniPiano.objects.get_or_create(azione=_formazione_del_piano, piano=piano)

                if cls.autorita_ok(piano) and \
                procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.necessaria:

                    procedura_avvio.notifica_genio_civile = False
                    procedura_avvio.save()

                    _conferenza_copianificazione = Azione(
                        tipologia=TIPOLOGIA_AZIONE.convocazione_conferenza_copianificazione,
                        attore=TIPOLOGIA_ATTORE.regione,
                        order=_order,
                        stato=STATO_AZIONE.necessaria
                    )
                    _conferenza_copianificazione.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_conferenza_copianificazione, piano=piano)

                    # TODO: verificare che parta la mail di conf. di Copianificazione
                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="conferenza_copianificazione")

                elif cls.autorita_ok(piano) and \
                procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.posticipata:

                    procedura_avvio.notifica_genio_civile = False
                    procedura_avvio.save()

                    _conferenza_copianificazione = Azione(
                        tipologia=TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione,
                        attore=TIPOLOGIA_ATTORE.comune,
                        order=_order,
                        stato=STATO_AZIONE.necessaria
                    )
                    _conferenza_copianificazione.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_conferenza_copianificazione, piano=piano)

                elif cls.autorita_ok(piano) and \
                procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.non_necessaria:

                    procedura_avvio.notifica_genio_civile = True
                    procedura_avvio.save()

                    _protocollo_genio_civile = Azione(
                        tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile,
                        attore=TIPOLOGIA_ATTORE.comune,
                        order=_order,
                        stato=STATO_AZIONE.attesa,
                        data=procedura_avvio.data_scadenza_risposta
                    )
                    _protocollo_genio_civile.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_protocollo_genio_civile, piano=piano)

                    _protocollo_genio_civile_id = Azione(
                        tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile_id,
                        attore=TIPOLOGIA_ATTORE.genio_civile,
                        order=_order,
                        stato=STATO_AZIONE.necessaria
                    )
                    _protocollo_genio_civile_id.save()
                    _order += 1
                    AzioniPiano.objects.get_or_create(azione=_protocollo_genio_civile_id, piano=piano)

                    # TODO: verificare che parta la mail di notifica al Genio Civile
                    # Notify Users
                    piano_phase_changed.send(
                        sender=Piano,
                        user=info.context.user,
                        piano=_piano,
                        message_type="protocollo_genio_civile")

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

                return AvvioPiano(
                    avvio_aggiornato=_procedura_avvio,
                    errors=[]
                )
            except BaseException as e:
                    tb = traceback.format_exc()
                    logger.error(tb)
                    return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class InvioProtocolloGenioCivile(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        _order = 0
        for _a in piano.azioni.all():
            _order += 1

        # - Update Action state accordingly
        if fase.nome == FASE.anagrafica:
            _protocollo_genio_civile = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE._protocollo_genio_civile).first()
            _protocollo_genio_civile_id = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile_id).first()
            if _protocollo_genio_civile_id and _protocollo_genio_civile_id.stato != STATO_AZIONE.nessuna:
                if piano.numero_protocollo_genio_civile and \
                piano.data_protocollo_genio_civile is None:
                    piano.data_protocollo_genio_civile = datetime.datetime.now(timezone.get_current_timezone())
                    piano.save()

                    _protocollo_genio_civile.stato = STATO_AZIONE.nessuna
                    _protocollo_genio_civile.data = datetime.datetime.now(timezone.get_current_timezone())
                    _protocollo_genio_civile.save()

                    _protocollo_genio_civile_id.stato = STATO_AZIONE.nessuna
                    _protocollo_genio_civile_id.data = datetime.datetime.now(timezone.get_current_timezone())
                    _protocollo_genio_civile_id.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

                return InvioProtocolloGenioCivile(
                    avvio_aggiornato=_procedura_avvio,
                    errors=[]
                )
            except BaseException as e:
                    tb = traceback.format_exc()
                    logger.error(tb)
                    return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
