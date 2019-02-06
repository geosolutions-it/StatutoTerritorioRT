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


# ############################################################################ #
# User
# ############################################################################ #
rules.add_rule(
    'strt_core.api.can_access_private_area',
    is_recognizable
)


# ############################################################################ #
# User <--> Piano
# ############################################################################ #
@rules.predicate
def can_access_piano(user, piano):
    return any(
        m.organization == piano.ente
        for m in user.memberships
    )


rules.add_rule(
    'strt_core.api.can_edit_piano',
    is_RUP & can_access_piano
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


rules.add_rule(
    'strt_core.api.fase_anagrafica_completa',
    is_draft & has_data_delibera & has_description & \
        has_delibera_comunale & has_soggetto_proponente
)


# ############################################################################ #
# Procedura VAS
# ############################################################################ #
