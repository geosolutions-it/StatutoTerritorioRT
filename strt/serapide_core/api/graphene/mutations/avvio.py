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
    unslugify,
    update_create_instance)

from serapide_core.signals import (
    piano_phase_changed,
)

from serapide_core.modello.models import (
    Fase, Qualifica, QualificaRichiesta,
    Piano,
    Azione,
    SoggettoOperante,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    PianoControdedotto,
    PianoRevPostCP,
    ConferenzaCopianificazione,

    isExecuted,
    needsExecution,
    ensure_fase,
    chiudi_azione,
    crea_azione,
)

from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_CONF_COPIANIFIZAZIONE,
)

from serapide_core.api.graphene import (types, inputs)
from serapide_core.api.graphene.mutations.vas import init_vas_procedure

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

                _procedura_avvio, created = ProceduraAvvio.objects.get_or_create(
                    piano=_piano, ente=_piano.ente)

                _procedura_avvio_data['id'] = _procedura_avvio.id
                _procedura_avvio_data['uuid'] = _procedura_avvio.uuid
                nuova_procedura_avvio = update_create_instance(_procedura_avvio, _procedura_avvio_data)

                _piano.procedura_avvio = nuova_procedura_avvio
                _piano.save()

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
        _role = info.context.session['role'] if 'role' in info.context.session else None
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
                 rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _ente), 'Comune')):
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
    def esiste_referente(cls, piano, tipologia):
        SoggettoOperante._default_manager.filter(piano=piano,)

    @classmethod
    def autorita_ok(cls, piano, qualifiche):
        # _res = False
        # _has_tipologia = False

        # TODO: check autorita_competente_vas, autorita_istituzionali, altri_destinatari
        if piano.soggetto_proponente and \
            piano.autorita_competente_vas.all().count() > 0 and \
            piano.autorita_istituzionali.all().count() >= 0 and \
            piano.altri_destinatari.all().count() >= 0 and \
            piano.soggetti_sca.all().count() >= 0:

            for qualifica in qualifiche:
                c = SoggettoOperante.objects.filter(piano=piano, qualifica_ufficio__qualifica=qualifica).count()
                if c > 0:
                    return True;

            # for _c in piano.soggetti_sca.all():
            #     _tipologia = _c.tipologia if contatto else \
            #         Contatto.attore(_c.user, tipologia=TIPOLOGIA_ATTORE[tipologia])
            #     if _tipologia.upper() == tipologia.upper():
            #         _has_tipologia = True
            #         break
            #
            # if not _has_tipologia:
            #     for _c in piano.autorita_istituzionali.all():
            #         _tipologia = _c.tipologia if contatto else \
            #             Contatto.attore(_c.user, tipologia=TIPOLOGIA_ATTORE[tipologia])
            #         if _tipologia.upper() == tipologia.upper():
            #             _has_tipologia = True
            #             break
            #
            # if not _has_tipologia:
            #     for _c in piano.altri_destinatari.all():
            #         _tipologia = _c.tipologia if contatto else \
            #             Contatto.attore(_c.user, tipologia=TIPOLOGIA_ATTORE[tipologia])
            #         if _tipologia.upper() == tipologia.upper():
            #             _has_tipologia = True
            #             break
            #
            # _res = _has_tipologia
        return False

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA);

        _avvio_procedimento = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_procedimento)
        if needsExecution(_avvio_procedimento):
            if not cls.autorita_ok(piano, [Qualifica.GC]):
                raise Exception(
                    "'%s' non presente fra i Soggetti Istituzionali." % unslugify(Qualifica.GC))

            if not cls.autorita_ok(piano, [Qualifica.PIAN, Qualifica.URB]):
                raise Exception(
                    "'%s' non presente fra i Soggetti Istituzionali." % unslugify([Qualifica.PIAN, Qualifica.URB]))

            chiudi_azione(_avvio_procedimento)

            crea_azione(Azione(
                            piano=piano,
                            tipologia=TIPOLOGIA_AZIONE.contributi_tecnici,
                            qualifica_richiesta=QualificaRichiesta.REGIONE,
                            stato=STATO_AZIONE.attesa,
                            data=procedura_avvio.data_scadenza_risposta
                        ))

            crea_azione(Azione(
                            piano=piano,
                            tipologia=TIPOLOGIA_AZIONE.richiesta_verifica_vas,
                            qualifica_richiesta=QualificaRichiesta.COMUNE,
                            stato=STATO_AZIONE.attesa
                        ))

            init_vas_procedure(piano)

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user \
                and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) \
                and rules.test_rule('strt_core.api.is_actor', _token
                                                            or (info.context.user, _role)
                                                            or (info.context.user, _organization), 'Comune'):
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
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class ContributiTecnici(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.contributi_tecnici

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):

        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_procedimento = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_procedimento)
        _contributi_tecnici = piano.getFirstAction(TIPOLOGIA_AZIONE.contributi_tecnici)

        if isExecuted(_avvio_procedimento) and needsExecution(_contributi_tecnici):

            chiudi_azione(_contributi_tecnici)

            crea_azione(piano,
                        Azione(
                            tipologia=TIPOLOGIA_AZIONE.formazione_del_piano,
                            qualifica_richiesta=QualificaRichiesta.COMUNE,
                            stato=STATO_AZIONE.necessaria
                        ))

            if procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.necessaria:

                procedura_avvio.notifica_genio_civile = False
                procedura_avvio.save()

                _cc, created = ConferenzaCopianificazione.objects.get_or_create(piano=piano)
                _cc.data_richiesta_conferenza = datetime.datetime.now(timezone.get_current_timezone())
                _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
                _cc.save()

                crea_azione(piano,
                            Azione(
                                tipologia=TIPOLOGIA_AZIONE.richiesta_integrazioni,
                                qualifica_richiesta=QualificaRichiesta.REGIONE,
                                stato=STATO_AZIONE.attesa
                            ))

                crea_azione(piano,
                            Azione(
                                tipologia=TIPOLOGIA_AZIONE.esito_conferenza_copianificazione,
                                qualifica_richiesta=QualificaRichiesta.REGIONE,
                                stato=STATO_AZIONE.attesa
                            ))

                return "conferenza_copianificazione"

            elif procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.posticipata:

                procedura_avvio.notifica_genio_civile = False
                procedura_avvio.save()

                _cc, created = ConferenzaCopianificazione.objects.get_or_create(piano=piano)
                _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
                _cc.save()

                crea_azione(piano,
                            Azione(
                                tipologia=TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione,
                                qualifica_richiesta=QualificaRichiesta.COMUNE,
                                stato=STATO_AZIONE.attesa
                            ))

                return None

            elif procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.non_necessaria:

                procedura_avvio.notifica_genio_civile = True
                procedura_avvio.save()

                crea_azione(piano,
                            Azione(
                                tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile,
                                qualifica_richiesta=QualificaRichiesta.GC,
                                stato=STATO_AZIONE.attesa
                            ))

                return "protocollo_genio_civile"

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Regione'):
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
        else:
            return GraphQLError(_("Forbidden"), code=403)


class RichiestaIntegrazioni(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.richiesta_integrazioni

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _richiesta_integrazioni = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_integrazioni)
        if needsExecution(_richiesta_integrazioni):

            chiudi_azione(_richiesta_integrazioni)

            if procedura_avvio.richiesta_integrazioni:
                crea_azione(Azione(
                                piano=piano,
                                tipologia=TIPOLOGIA_AZIONE.integrazioni_richieste,
                                qualifica_richiesta=QualificaRichiesta.COMUNE,
                                stato=STATO_AZIONE.attesa
                            ))
            else:
                _conferenza_copianificazione_attiva = \
                    needsExecution(piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione)) or \
                    needsExecution(piano.getFirstAction(TIPOLOGIA_AZIONE.esito_conferenza_copianificazione))

                _formazione_del_piano = piano.getFirstAction(TIPOLOGIA_AZIONE.formazione_del_piano)
                _procedura_vas = ProceduraVAS.objects.filter(piano=piano).last()
                if not _procedura_vas or _procedura_vas.conclusa:
                    if not _conferenza_copianificazione_attiva and isExecuted(_formazione_del_piano):
                        piano.chiudi_pendenti(attesa=True, necessaria=False)

                procedura_avvio.conclusa = True
                procedura_avvio.save()

                procedura_adozione, created = ProceduraAdozione.objects.get_or_create(
                    piano=piano, ente=piano.ente)

                PianoControdedotto.objects.get_or_create(piano=piano)
                PianoRevPostCP.objects.get_or_create(piano=piano)

                piano.procedura_adozione = procedura_adozione
                piano.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user \
            and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) \
            and rules.test_rule('strt_core.api.is_actor', _token  \
                                                        or (info.context.user, _role) \
                                                        or (info.context.user, _organization), 'Regione'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="richiesta_integrazioni")

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

                return RichiestaIntegrazioni(
                    avvio_aggiornato=_procedura_avvio,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class IntegrazioniRichieste(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.integrazioni_richieste

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA)

        _integrazioni_richieste = piano.getFirstAction(TIPOLOGIA_AZIONE.integrazioni_richieste)
        if needsExecution(_integrazioni_richieste):
            chiudi_azione(_integrazioni_richieste)

            _conferenza_copianificazione_attiva = False

            _richiesta_conferenza_copianificazione = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione)
            if needsExecution(_richiesta_conferenza_copianificazione):
                _conferenza_copianificazione_attiva = True

            _esito_conferenza_copianificazione = piano.getFirstAction(TIPOLOGIA_AZIONE.esito_conferenza_copianificazione)
            if needsExecution(_esito_conferenza_copianificazione):
                _conferenza_copianificazione_attiva = True

            _formazione_del_piano = piano.getFirstAction(TIPOLOGIA_AZIONE.formazione_del_piano)
            _procedura_vas = ProceduraVAS.objects.filter(piano=piano).last()
            if not _procedura_vas or _procedura_vas.conclusa:
                if not _conferenza_copianificazione_attiva and isExecuted(_formazione_del_piano):
                    piano.chiudi_pendenti(attesa=True, necessaria=False)

            procedura_avvio.conclusa = True
            procedura_avvio.save()

            procedura_adozione, created = ProceduraAdozione.objects.get_or_create(piano=piano, ente=piano.ente)
            PianoControdedotto.objects.get_or_create(piano=piano)
            PianoRevPostCP.objects.get_or_create(piano=piano)

            piano.procedura_adozione = procedura_adozione
            piano.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and \
                rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="integrazioni_richieste")

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

                return IntegrazioniRichieste(
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

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.protocollo_genio_civile

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Update Action state accordingly
        ensure_fase(fase, Fase.ANAGRAFICA)

        _protocollo_genio_civile = piano.getFirstAction(TIPOLOGIA_AZIONE.protocollo_genio_civile)
        if needsExecution(_protocollo_genio_civile):
            if piano.numero_protocollo_genio_civile:
                piano.data_protocollo_genio_civile = datetime.datetime.now(timezone.get_current_timezone())
                piano.save()

                chiudi_azione(_protocollo_genio_civile)

                # controllo se procedura di avvio conclusa
                _formazione_del_piano = piano.getFirstAction(TIPOLOGIA_AZIONE.formazione_del_piano)
                _integrazioni_richieste = piano.getFirstAction(TIPOLOGIA_AZIONE.integrazioni_richieste)

                if isExecuted(_formazione_del_piano) and \
                    (not procedura_avvio.richiesta_integrazioni or (isExecuted(_integrazioni_richieste))):

                    _procedura_vas = ProceduraVAS.objects.filter(piano=piano).last()
                    if not _procedura_vas or _procedura_vas.conclusa:
                        piano.chiudi_pendenti(attesa=True, necessaria=False)
                    procedura_avvio.conclusa = True
                    procedura_avvio.save()

                    procedura_adozione, created = ProceduraAdozione.objects.get_or_create(piano=piano, ente=piano.ente)
                    PianoControdedotto.objects.get_or_create(piano=piano)
                    PianoRevPostCP.objects.get_or_create(piano=piano)

                    piano.procedura_adozione = procedura_adozione
                    piano.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'GENIO_CIVILE'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

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


class RichiestaConferenzaCopianificazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_procedimento = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_procedimento)
        if isExecuted(_avvio_procedimento):
            if procedura_avvio.conferenza_copianificazione == TIPOLOGIA_CONF_COPIANIFIZAZIONE.posticipata:

                _richiesta_cc = piano.getFirstAction(TIPOLOGIA_AZIONE.richiesta_conferenza_copianificazione)
                if needsExecution(_richiesta_cc):

                    chiudi_azione(_richiesta_cc) # TODO check: original code did not set timestamp

                    procedura_avvio.notifica_genio_civile = False
                    procedura_avvio.save()

                    _cc = ConferenzaCopianificazione.objects.get(piano=piano)
                    _cc.data_richiesta_conferenza = datetime.datetime.now(timezone.get_current_timezone())
                    _cc.data_scadenza_risposta = procedura_avvio.data_scadenza_risposta
                    _cc.save()

                    crea_azione(piano,
                                Azione(
                                    tipologia=TIPOLOGIA_AZIONE.richiesta_integrazioni,
                                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                                    stato=STATO_AZIONE.attesa
                                ))

                    crea_azione(piano,
                                Azione(
                                    tipologia=TIPOLOGIA_AZIONE.esito_conferenza_copianificazione,
                                    qualifica_richiesta=QualificaRichiesta.REGIONE,
                                    stato=STATO_AZIONE.attesa,
                                    data=procedura_avvio.data_scadenza_risposta
                                ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Comune'):
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
        else:
            return GraphQLError(_("Forbidden"), code=403)


class ChiusuraConferenzaCopianificazione(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    avvio_aggiornato = graphene.Field(types.ProceduraAvvioNode)

    @staticmethod
    def action():
        return TIPOLOGIA_AZIONE.esito_conferenza_copianificazione

    @staticmethod
    def procedura(piano):
        return piano.procedura_avvio

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_avvio, user):
        # Update Azioni Piano
        # - Complete Current Actions
        # - Update Action state accordingly

        ensure_fase(fase, Fase.ANAGRAFICA)

        _avvio_procedimento = piano.getFirstAction(TIPOLOGIA_AZIONE.avvio_procedimento)
        if isExecuted(_avvio_procedimento):

            _esito_cc = piano.getFirstAction(TIPOLOGIA_AZIONE.esito_conferenza_copianificazione)
            if needsExecution(_esito_cc):

                chiudi_azione(_esito_cc) # TODO: check: original code did not set timestamp

                procedura_avvio.notifica_genio_civile = True
                procedura_avvio.save()

                _cc = ConferenzaCopianificazione.objects.get(piano=piano)
                _cc.data_chiusura_conferenza = datetime.datetime.now(timezone.get_current_timezone())
                _cc.save()

                crea_azione(piano,
                            Azione(
                                tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile,
                                qualifica_richiesta=QualificaRichiesta.GC,
                                stato=STATO_AZIONE.attesa,
                                data=procedura_avvio.data_scadenza_risposta
                            ))

    @classmethod
    def mutate(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _piano = _procedura_avvio.piano
        _role = info.context.session['role'] if 'role' in info.context.session else None
        _token = info.context.session['token'] if 'token' in info.context.session else None
        _organization = _piano.ente
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _role) or (info.context.user, _organization), 'Regione'):
            try:
                cls.update_actions_for_phase(_piano.fase, _piano, _procedura_avvio, info.context.user)

                # Notify Users
                piano_phase_changed.send(
                    sender=Piano,
                    user=info.context.user,
                    piano=_piano,
                    message_type="protocollo_genio_civile")

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

                return ChiusuraConferenzaCopianificazione(
                    avvio_aggiornato=_procedura_avvio,
                    errors=[]
                )
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
