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

from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path


urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    url(r'^serapide/', include('serapide_core.api.urls')),
]
