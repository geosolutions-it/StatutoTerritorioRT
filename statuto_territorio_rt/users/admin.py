#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from shared_model.models import AppUser


admin.site.register(AppUser, UserAdmin)