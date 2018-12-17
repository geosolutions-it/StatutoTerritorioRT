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

from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(BaseAppConfig):

    name = "serapide_core"
    label = "serapide_core"
    verbose_name = _("Django SERAPIDE - Core")

    def ready(self):
        """Connect relevant signals to their corresponding handlers"""
        """
            NO SIGNALS DEFINED YET
        """
        super(AppConfig, self).ready()
