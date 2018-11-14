#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.urls import path, reverse_lazy
from .views import (
    SerapideView, GeoportalView, OpendataView, GlossaryView
)


urlpatterns = [
    path('serapide/', SerapideView.as_view(), name='serapide'),
    path('geoportal/', GeoportalView.as_view(), name='geoportal'),
    path('opendata/', OpendataView.as_view(), name='opendata'),
    path('glossary/', GlossaryView.as_view(), name='glossary'),
]
