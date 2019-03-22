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

from strt_users.models import (
    Token,
    Organization)

from serapide_core.modello.models import (
    Contatto,
    PianoAuthTokens)


# ############################################################################ #
# User
# ############################################################################ #
@rules.predicate
def can_access_piano(user, piano):
    _has_access = any(
        m.organization == piano.ente
        for m in user.memberships
    )

    if not _has_access:
        _tokens = Token.objects.filter(user=user)
        for _t in _tokens:
            if not _t.is_expired():
                _allowed_pianos = [_pt.piano for _pt in PianoAuthTokens.objects.filter(token__key=_t.key)]
                _has_access = piano in _allowed_pianos
                if _has_access:
                    break
    return _has_access


@rules.predicate
def is_actor_for_token(token, actor):
    _attore = None
    if token and \
    (isinstance(token, str) or isinstance(token, Token)):
        token = Token.objects.get(key=token)
        _attore = Contatto.attore(token.user, token=token.key)

    if _attore is None:
        return False
    else:
        return (_attore.lower() == actor.lower())


@rules.predicate
def is_actor_for_organization(user_info, actor):
    _user = user_info[0]
    _organization = user_info[1]
    _attore = None
    if _user and \
    _organization and isinstance(_organization, Organization):
        _attore = Contatto.attore(_user, organization=_organization.code)

    if _attore is None:
        return False
    else:
        return (_attore == actor)
