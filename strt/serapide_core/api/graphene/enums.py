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

import graphene


class StrtEnumNode(graphene.ObjectType):

    value = graphene.String()
    label = graphene.String()


# class FasePiano(StrtEnumNode):
#     pass


class TipologiaVAS(StrtEnumNode):
    pass


class TipologiaPiano(StrtEnumNode):
    pass


class TipologiaContatto(StrtEnumNode):
    pass


class TipologiaConferenzaCopianificazione(StrtEnumNode):
    pass
