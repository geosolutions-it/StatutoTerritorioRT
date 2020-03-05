# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import rules
import logging
from django.conf import settings

from serapide_core.api.auth.user import has_profile
from strt_users.enums import Profilo

logger = logging.getLogger(__name__)

@rules.predicate
def is_superuser(user):
    return user.is_superuser


@rules.predicate
def is_recognizable(user):
    return not user.is_anonymous \
           and user.is_active \
           and user.is_authenticated


@rules.predicate
def is_member(user, user_memberships=None):
    # TODO: replace
    logger.warning("TODO: replace RULE is_member")
    return has_profile(user, Profilo.OPERATORE)
    # if user_memberships:
    #     return any([mu.member == user for mu in user_memberships])
    # else:
    #     return len(list(user.memberships)) > 0


@rules.predicate
def is_responsabile_ISIDE(user):
    # TODO: replace
    logger.warning("TODO: replace RULE is_responsabile_ISIDE")
    return has_profile(user, Profilo.ADMIN_PORTALE)
    # return any(
    #     m.type.code == settings.RESPONSABILE_ISIDE_CODE
    #     for m in user.memberships
    # )


@rules.predicate
def is_RUP(user):
    # TODO: replace
    logger.warning("TODO: replace RULE is_RUP")
    return has_profile(user, Profilo.ADMIN_ENTE)
    # return any(
    #     m.type.code == settings.RUP_CODE
    #     for m in user.memberships
    # )


@rules.predicate
def is_member_of(user, organization):
    return any(
        m.organization == organization
        for m in user.memberships
    )


rules.add_perm(
    'strt_users.can_manage_users',
    is_recognizable & (is_responsabile_ISIDE | is_RUP)
)

rules.add_perm(
    'strt_users.can_access_private_area',
    is_recognizable
)

rules.add_perm(
    'strt_users.can_access_serapide',
    is_recognizable & is_member
)

rules.add_rule(
    'strt_users.is_superuser',
    is_recognizable & is_superuser
)

rules.add_rule(
    'strt_users.is_RUP_of',
    is_recognizable & is_RUP & is_member_of
)
