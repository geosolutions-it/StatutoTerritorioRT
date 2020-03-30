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

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# APIs imports
from strt_geoportale import urls as geoportale_urls
from serapide_core import urls as serapide_code_urls

# Dajngo admin
urlpatterns = [
    path('admin/', admin.site.urls),
]

# Apps urls
urlpatterns += [
    path('', include('strt_portal.urls')),
    path('users/', include('strt_users.urls'))
]

# APIs urls
urlpatterns += [
    path('', include(serapide_code_urls)),
]

# Geoportale urls
urlpatterns += [
    path('geoportale/', include(geoportale_urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
