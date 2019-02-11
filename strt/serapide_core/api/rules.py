# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import os
import rules
from django.conf import settings

from strt_users.rules import (is_RUP,
                              is_recognizable,
                              is_responsabile_ISIDE)

from ..modello.enums import (FASE,
                             TIPOLOGIA_CONTATTO,
                             TIPOLOGIA_PIANO,
                             TIPOLOGIA_VAS)

from ..modello.models import ProceduraVAS


# ############################################################################ #
# User <--> Piano
# ############################################################################ #
@rules.predicate
def can_access_piano(user, piano):
    return any(
        m.organization == piano.ente
        for m in user.memberships
    )


# ############################################################################ #
# Piano
# ############################################################################ #
@rules.predicate
def is_draft(piano):
    return piano.fase.nome == FASE.draft


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


# ############################################################################ #
# Procedura VAS
# ############################################################################ #
@rules.predicate
def procedura_vas_is_valid(piano, procedura_vas):
    if procedura_vas.piano == piano:
        if piano.fase.nome == FASE.draft:
            if procedura_vas.tipologia == TIPOLOGIA_VAS.semplificata:
                if procedura_vas.risorse.filter(tipo='vas_semplificata').count() == 1 and \
                    procedura_vas.risorse.get(tipo='vas_semplificata').dimensione > 0 and \
                        procedura_vas.risorse.get(tipo='vas_semplificata').file and \
                            os.path.exists(procedura_vas.risorse.get(tipo='vas_semplificata').file.path):
                                return True
                return False
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.verifica:
                if procedura_vas.risorse.filter(tipo='vas_verifica').count() > 0:
                    return procedura_vas.risorse.filter(tipo='vas_verifica').count() > 0 and \
                        all(
                            r.dimensione > 0 and r.file and os.path.exists(r.file.path)
                            for r in procedura_vas.risorse.filter(tipo='vas_verifica')
                        )
                return False
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento:
                return (
                    piano.autorita_competente_vas.count() > 0 and \
                        piano.soggetti_sca.count() > 0
                )
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                print("NON NECESSARIA")
                return True
            else:
                return False
    return False


# ############################################################################ #
# RULES
# ############################################################################ #

"""
- TODO:
    . Add "notifications" on change fase operations
    . Add backend consistency rules-checks accordingly to the fase, e.g.:
        * Date, Description, Delibera ... cannot be changed after "DRAFT" fase
        ...
"""
rules.add_rule(
    'strt_core.api.can_access_private_area',
    is_recognizable
)

rules.add_rule(
    'strt_core.api.can_edit_piano',
    is_RUP & can_access_piano
)

rules.add_rule(
    'strt_core.api.fase_anagrafica_completa',
    is_draft & has_data_delibera & has_description & \
        has_delibera_comunale & has_soggetto_proponente & \
            has_procedura_vas & procedura_vas_is_valid
)
