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

from serapide_core.modello.enums import (
    Fase,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,)

from serapide_core.modello.models import (
    Piano,
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


@rules.predicate
def has_data_delibera(piano):
    return piano.data_delibera is not None


@rules.predicate
def has_description(piano):
    return piano.descrizione is not None


@rules.predicate
def has_delibera_comunale(piano):
    return (
        piano.risorse.count() > 0 and
        piano.risorse.filter(tipo='delibera', archiviata=False).count() == 1 and
        piano.risorse.get(tipo='delibera', archiviata=False).dimensione > 0 and
        piano.risorse.get(tipo='delibera', archiviata=False).file and
        os.path.exists(piano.risorse.get(tipo='delibera', archiviata=False).file.path)
    )


@rules.predicate
def has_soggetto_proponente(piano):
    return piano.soggetto_proponente is not None


@rules.predicate
def has_procedura_vas(piano):
    return ProceduraVAS.objects.filter(piano=piano).count() > 0


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
    _procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
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
    _procedura_adozione_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
        return True
    return _procedura_adozione_vas.conclusa


@rules.predicate
def approvazione_piano_conclusa(piano):
    _procedura_approvazione = ProceduraApprovazione.objects.filter(piano=piano).first()
    return _procedura_approvazione.conclusa


@rules.predicate
def has_pending_alerts(piano):
    _alert_states = [STATO_AZIONE.necessaria]
    return piano.azioni.filter(stato__in=_alert_states).count() > 1
