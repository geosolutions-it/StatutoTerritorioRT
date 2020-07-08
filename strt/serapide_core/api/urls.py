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

from django.conf.urls import url

from ..schema import schema
# from graphene_django.views import GraphQLView
from .views import (
    PrivateGraphQLView,
    geo_search,
    geo_groups,
    geo_get,
)

urlpatterns = [
    url(r'^graphql', PrivateGraphQLView.as_view(graphiql=True, schema=schema)),
    url(r'^geo/map/search$', geo_search),
    url(r'^geo/map/(?P<pk>.+)$', geo_get),
    url(r'^geo/groups$', geo_groups),
]
