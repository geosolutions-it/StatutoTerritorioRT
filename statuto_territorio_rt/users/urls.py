#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.urls import path, include
from .views import registrazionView


urlpatterns = [
    path('registration/', registrazionView, name='registration'),
    path('', include('django.contrib.auth.urls')),
]