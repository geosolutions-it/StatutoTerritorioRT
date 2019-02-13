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

from django.utils.translation import ugettext_lazy as _

from .notifications_helper import NotificationsAppConfigBase


def run_setup_hooks(*args, **kwargs):
    pass


class AppConfig(NotificationsAppConfigBase):

    name = "serapide_core"
    label = "serapide_core"
    verbose_name = _("Django SERAPIDE - Core")

    def ready(self):
        """Connect relevant signals to their corresponding handlers"""
        super(AppConfig, self).ready()
        run_setup_hooks()
