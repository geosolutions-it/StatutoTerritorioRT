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

from serapide_core.modello.enums import FASE, STATO_AZIONE
from serapide_core.modello.models import Piano, ProceduraVAS


# ############################################################################ #
# Piano
# ############################################################################ #
@rules.predicate
def is_draft(user, obj):
    if isinstance(obj, Piano):
        return obj.fase.nome == FASE.draft
    elif isinstance(obj, ProceduraVAS):
        return obj.piano.fase.nome == FASE.draft
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
        piano.risorse.filter(tipo='delibera').count() == 1 and
        piano.risorse.get(tipo='delibera').dimensione > 0 and
        piano.risorse.get(tipo='delibera').file and
        os.path.exists(piano.risorse.get(tipo='delibera').file.path)
    )


@rules.predicate
def has_soggetto_proponente(piano):
    return piano.soggetto_proponente is not None


@rules.predicate
def has_procedura_vas(piano):
    return ProceduraVAS.objects.filter(piano=piano).count() == 1


@rules.predicate
def has_pending_alerts(piano):
    _alert_states = [STATO_AZIONE.attesa, STATO_AZIONE.necessaria]
    return piano.azioni.filter(stato__in=_alert_states).count() > 0
