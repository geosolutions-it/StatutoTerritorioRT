# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2020, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################
from django.shortcuts import render
from serapide_core.api.auth.user import (
    has_profile
)
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(has_profile)
def geportale_home(request):
    return render(request, "geoportale/geoportale.html")
