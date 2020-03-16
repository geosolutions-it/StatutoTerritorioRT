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

import os
import rules
import logging


from serapide_core.modello.enums import TipoRisorsa
import serapide_core.api.auth.vas as auth_vas

from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TipologiaVAS,
    TIPOLOGIA_AZIONE,)


from serapide_core.modello.models import (
    Piano, Azione,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    ProceduraAdozioneVAS,
    ProceduraApprovazione,)

logger = logging.getLogger(__name__)

# ############################################################################ #
# Piano
# ############################################################################ #
@rules.predicate
def is_draft(user, obj):
    if isinstance(obj, Piano):
        return obj.fase == Fase.DRAFT
    elif isinstance(obj, ProceduraVAS):
        return obj.piano.fase == Fase.DRAFT
    else:
        return False


@rules.predicate
def is_anagrafica(user, obj):
    if isinstance(obj, Piano):
        return obj.fase == Fase.ANAGRAFICA
    elif isinstance(obj, ProceduraVAS):
        return obj.piano.fase == Fase.ANAGRAFICA
    else:
        return False


@rules.predicate
def is_avvio(user, obj):
    if isinstance(obj, Piano):
        return obj.fase == Fase.AVVIO
    elif isinstance(obj, ProceduraVAS):
        return obj.piano.fase == Fase.AVVIO
    else:
        return False


@rules.predicate
def is_adozione(user, obj):
    if isinstance(obj, Piano):
        return obj.fase == Fase.ADOZIONE
    elif isinstance(obj, ProceduraVAS):
        return obj.piano.fase == Fase.ADOZIONE
    else:
        return False


# @rules.predicate
# def has_data_delibera(piano):
#     return piano.data_delibera is not None


# @rules.predicate
# def has_description(piano):
#     return piano.descrizione is not None


@rules.predicate
def has_delibera_comunale(piano):
    return (
        piano.risorse.count() > 0 and
        piano.risorse.filter(tipo=TipoRisorsa.DELIBERA.value, archiviata=False).count() == 1 and
        piano.risorse.get(tipo=TipoRisorsa.DELIBERA.value, archiviata=False).dimensione > 0 and
        piano.risorse.get(tipo=TipoRisorsa.DELIBERA.value, archiviata=False).file and
        os.path.exists(piano.risorse.get(tipo=TipoRisorsa.DELIBERA.value, archiviata=False).file.path)
    )


# @rules.predicate
# def has_soggetto_proponente(piano):
#     return piano.soggetto_proponente is not None


# @rules.predicate
# def has_procedura_vas(piano):
#     return ProceduraVAS.objects.filter(piano=piano).count() > 0


@rules.predicate
def has_procedura_avvio(piano):
    return ProceduraAvvio.objects.filter(piano=piano).count() > 0


@rules.predicate
def has_procedura_adozione(piano):
    return ProceduraAdozione.objects.filter(piano=piano).count() > 0


@rules.predicate
def has_procedura_adozione_vas(piano):
    return ProceduraAdozioneVAS.objects.filter(piano=piano).count() > 0


@rules.predicate
def has_procedura_approvazione(piano):
    return ProceduraApprovazione.objects.filter(piano=piano).count() > 0


@rules.predicate
def protocollo_genio_inviato(piano):
    az = piano.getFirstAction(TIPOLOGIA_AZIONE.protocollo_genio_civile)
    return az and az.stato == STATO_AZIONE.nessuna


@rules.predicate
def formazione_piano_conclusa(piano):
    az = piano.getFirstAction(TIPOLOGIA_AZIONE.formazione_del_piano)
    return az and az.stato == STATO_AZIONE.nessuna


@rules.predicate
def vas_piano_conclusa(piano):
    _procedura_vas = ProceduraVAS.objects.filter(piano=piano).first()
    if not _procedura_vas or \
    _procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
        return True
    return _procedura_vas.conclusa


@rules.predicate
def avvio_piano_conclusa(piano):
    _procedura_avvio = ProceduraAvvio.objects.filter(piano=piano).first()
    return _procedura_avvio.conclusa


@rules.predicate
def adozione_piano_conclusa(piano):
    _procedura_adozione = ProceduraAdozione.objects.filter(piano=piano).first()
    return _procedura_adozione.conclusa


@rules.predicate
def adozione_vas_piano_conclusa(piano):
    _procedura_adozione_vas = ProceduraAdozioneVAS.objects.filter(piano=piano).first()
    return not _procedura_adozione_vas or _procedura_adozione_vas.conclusa


@rules.predicate
def approvazione_piano_conclusa(piano):
    _procedura_approvazione = ProceduraApprovazione.objects.filter(piano=piano).first()
    return _procedura_approvazione.conclusa


@rules.predicate
def has_pending_alerts(piano):
    _alert_states = [STATO_AZIONE.necessaria]
    return Azione.objects.filter(piano=piano, stato__in=_alert_states).exists()

def get_pending_alerts(piano):
    _alert_states = [STATO_AZIONE.necessaria]
    return Azione.objects.filter(piano=piano, stato__in=_alert_states)


def load_pending_alerts(piano:Piano, msg:list):
    # FIXME il saltare la prima azione è un pessimo hack già esistente.
    # dovrebbe servire solo per il create_piano. Da fixare!!! magari con un nuovo tipoazione=AUTO?

    azcnt = 0
    for azione in get_pending_alerts(piano):
        if azcnt == 0:
            logger.warning("Skipping pending alert {}".format(azione))
        else:
            msg.append("Azione non completata: {} [{}]".format(azione.tipologia, azione.qualifica_richiesta.name))
        azcnt = azcnt + 1


def is_eligible_for_promotion(piano:Piano):

    logger.warning("Is eligible for promotion {p} {f}".format(p=piano, f=piano.fase))

    msg = []
    load_pending_alerts(piano, msg)

    if piano.fase == Fase.DRAFT:

        # rules.add_rule('strt_core.api.fase_anagrafica_completa',
        # ~has_pending_alerts &
        # is_draft &
        # has_data_delibera &
        # has_description &
        # has_delibera_comunale &
        # has_soggetto_proponente &
        # has_procedura_vas &
        # vas_rules.procedura_vas_is_valid

        # load_pending_alerts(piano, msg)
        # if not is_draft(piano):
        #     msg.append("Piano non in stato di bozza")
        if piano.data_delibera is None:
            msg.append("Data delibera non impostata")
        if piano.descrizione is None:
            msg.append("Descrizione non impostata")
        if not has_delibera_comunale(piano):
            msg.append("Delibera comunale mancante")
        if piano.soggetto_proponente is None:
            msg.append("Soggetto proponente mancante")
        if not ProceduraVAS.objects.filter(piano=piano).exists():
            msg.append("Procedura VAS mancante")

        vas_ok, vas_msg = auth_vas.procedura_vas_is_valid(piano)
        if not vas_ok:
            msg = msg + vas_msg

        return len(msg) == 0, msg

    elif piano.fase == Fase.ANAGRAFICA:

        # rules.add_rule('strt_core.api.fase_avvio_completa',
        #     ~has_pending_alerts &
        #     is_anagrafica &
        #     protocollo_genio_inviato &
        #     formazione_piano_conclusa &
        #     has_procedura_avvio &
        #     avvio_piano_conclusa &
        #     (~has_procedura_vas | vas_piano_conclusa)
        # )

        # if has_pending_alerts(piano):
        #     msg.append("Ci sono azioni non ancora completate")
        if not protocollo_genio_inviato(piano):
            msg.append("Protocollo Genio Civile mancante")
        if not formazione_piano_conclusa(piano):
            msg.append("Formazione piano non conclusa")
        if not has_procedura_avvio(piano):
            msg.append("Procedura di avvio mancante")
        if not avvio_piano_conclusa(piano):
            msg.append("Procedura di avvio non conclusa")
        if not vas_piano_conclusa(piano):
            msg.append("Procedura VAS non conclusa")

        return len(msg) == 0, msg

    elif piano.fase == Fase.AVVIO:

        # rules.add_rule(
        #     'strt_core.api.fase_adozione_completa',
        #     ~has_pending_alerts &
        #     is_avvio &
        #     has_procedura_adozione &
        #     adozione_piano_conclusa &
        #     (~has_procedura_adozione_vas | adozione_vas_piano_conclusa)
        # )

        # if has_pending_alerts(piano):
        #     msg.append("Ci sono azioni non ancora completate")

        if not has_procedura_adozione(piano):
            msg.append("Procedura di adpzione mancante")
        if not adozione_piano_conclusa(piano):
            msg.append("Procedura di adozione non conclusa")
        if not adozione_vas_piano_conclusa(piano):
            msg.append("Procedura AdozioneVAS non conclusa")

        return len(msg) == 0, msg

    raise Exception('NOT IMPLEMENTED YET')



#
# rules.add_rule(
#     'strt_core.api.fase_approvazione_completa',
#     ~has_pending_alerts &
#     is_adozione &
#     has_procedura_approvazione &
#     approvazione_piano_conclusa
# )
