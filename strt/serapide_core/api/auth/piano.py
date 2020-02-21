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
    _protocollo_genio_civile = piano.getFirstAction(TIPOLOGIA_AZIONE.protocollo_genio_civile)

    if not _protocollo_genio_civile:
        return False

    return _protocollo_genio_civile.stato == STATO_AZIONE.nessuna


@rules.predicate
def formazione_piano_conclusa(piano):
    _formazione_del_piano = piano.azioni.filter(
        tipologia=TIPOLOGIA_AZIONE.formazione_del_piano).first()

    if not _formazione_del_piano:
        return False

    return _formazione_del_piano.stato == STATO_AZIONE.nessuna


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
    if not _procedura_adozione_vas or \
    _procedura_adozione_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
        return True
    return _procedura_adozione_vas.conclusa


@rules.predicate
def approvazione_piano_conclusa(piano):
    _procedura_approvazione = ProceduraApprovazione.objects.filter(piano=piano).first()
    return _procedura_approvazione.conclusa


@rules.predicate
def has_pending_alerts(piano):
    _alert_states = [STATO_AZIONE.necessaria]
    return Azione.objects.filter(piano=piano, stato__in=_alert_states).count() > 1


def is_eligible_for_promotion(piano:Piano):

    msg = []

    if piano.fase == Fase.DRAFT:
        # 'strt_core.api.fase_anagrafica_completa',
    # ~has_pending_alerts &
    # is_draft &
    # has_data_delibera &
    # has_description &
    # has_delibera_comunale &
    # has_soggetto_proponente &
    # has_procedura_vas &
    # vas_rules.procedura_vas_is_valid
        if has_pending_alerts(piano):
            msg.append("Ci sono azioni non ancora completate")
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
        if ProceduraVAS.objects.filter(piano=piano).count() == 0:
            msg.append("Procedura VAS mancante")

        vas_ok, vas_msg = auth_vas.procedura_vas_is_valid(piano)
        if not vas_ok:
            msg = msg + vas_msg

        return len(msg) == 0, msg

    raise Exception('NOT IMPLEMENTED YET')

# rules.add_rule(
#     'strt_core.api.fase_avvio_completa',
#     ~has_pending_alerts &
#     is_anagrafica &
#     protocollo_genio_inviato &
#     formazione_piano_conclusa &
#     has_procedura_avvio &
#     avvio_piano_conclusa &
#     (~has_procedura_vas | vas_piano_conclusa)
# )
#
# rules.add_rule(
#     'strt_core.api.fase_adozione_completa',
#     ~has_pending_alerts &
#     is_avvio &
#     has_procedura_adozione &
#     adozione_piano_conclusa &
#     (~has_procedura_adozione_vas | adozione_vas_piano_conclusa)
# )
#
# rules.add_rule(
#     'strt_core.api.fase_approvazione_completa',
#     ~has_pending_alerts &
#     is_adozione &
#     has_procedura_approvazione &
#     approvazione_piano_conclusa
# )
