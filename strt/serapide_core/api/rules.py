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

from strt_users.rules import (
    is_RUP,
    is_recognizable,
    is_responsabile_ISIDE
)

from .auth import (
    user,
    piano,
    vas
)


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
    user.can_access_piano & is_RUP
)

rules.add_rule(
    'strt_core.api.can_update_piano',
    user.can_access_piano & piano.is_draft
)

rules.add_rule(
    'strt_core.api.fase_anagrafica_completa',
    piano.is_draft & piano.has_data_delibera & piano.has_description & \
        piano.has_delibera_comunale & piano.has_soggetto_proponente & \
            piano.has_procedura_vas & vas.procedura_vas_is_valid
)
