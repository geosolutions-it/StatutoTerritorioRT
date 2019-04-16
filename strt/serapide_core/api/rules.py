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
    # is_responsabile_ISIDE
)

from .auth import (
    user as user_rules,
    piano as piano_rules,
    vas as vas_rules
)


# ############################################################################ #
# RULES
# ############################################################################ #
rules.add_rule(
    'strt_core.api.can_access_private_area',
    is_recognizable
)

rules.add_rule(
    'strt_core.api.can_edit_piano',
    is_RUP | user_rules.can_access_piano
)

rules.add_rule(
    'strt_core.api.is_actor',
    user_rules.is_actor_for_token | user_rules.is_actor_for_organization
)

rules.add_rule(
    'strt_core.api.can_update_piano',
    user_rules.can_access_piano
)

rules.add_rule(
    'strt_core.api.parere_sca_ok',
    vas_rules.parere_sca_ok
)

rules.add_rule(
    'strt_core.api.parere_verifica_vas_ok',
    vas_rules.parere_verifica_vas_ok
)

rules.add_rule(
    'strt_core.api.fase_anagrafica_completa',
    ~piano_rules.has_pending_alerts &
    piano_rules.is_draft &
    piano_rules.has_data_delibera &
    piano_rules.has_description &
    piano_rules.has_delibera_comunale &
    piano_rules.has_soggetto_proponente &
    piano_rules.has_procedura_vas &
    vas_rules.procedura_vas_is_valid
)

rules.add_rule(
    'strt_core.api.fase_avvio_completa',
    ~piano_rules.has_pending_alerts &
    piano_rules.is_anagrafica &
    vas_rules.procedura_vas_is_valid &
    piano_rules.has_procedura_avvio &
    piano_rules.protocollo_genio_inviato &
    piano_rules.formazione_piano_conclusa &
    piano_rules.avvio_piano_conclusa
)

rules.add_rule(
    'strt_core.api.fase_adozione_completa',
    ~piano_rules.has_pending_alerts &
    piano_rules.is_avvio &
    piano_rules.has_procedura_adozione &
    piano_rules.adozione_piano_conclusa
)
