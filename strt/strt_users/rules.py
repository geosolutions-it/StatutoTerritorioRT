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

import rules
from django.conf import settings


@rules.predicate
def is_recognizable(user):
    return not user.is_anonymous \
           and user.is_active \
           and user.is_authenticated

@rules.predicate
def is_member(user, user_memberships=None):
    if user_memberships:
        return any([mu.member == user for mu in user_memberships])
    else:
        return len(list(user.memberships)) > 0

@rules.predicate
def is_responsabile_ISIDE(user):
    return any(
        m.type.code == settings.RESPONSABILE_ISIDE_CODE
        for m in user.memberships
    )

@rules.predicate
def is_RUP(user):
    return any(
        m.type.code == settings.RUP_CODE
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
    is_recognizable & is_member & ~is_responsabile_ISIDE
)
