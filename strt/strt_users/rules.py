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
def is_responsabile_ISIDE(user):
    return all(
        m.type.code in settings.RESPONSABILE_ISIDE_CODES
        for m in user.memberships
    )

@rules.predicate
def is_RUP(user):
    return all(
        m.type.code in settings.RUP_CODES
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