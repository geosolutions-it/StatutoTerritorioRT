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


# ############################################################################ #
# User
# ############################################################################ #
@rules.predicate
def can_access_piano(user, piano):
    return any(
        m.organization == piano.ente
        for m in user.memberships
    )
