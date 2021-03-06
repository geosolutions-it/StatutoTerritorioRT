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

from django.utils.translation import ugettext_lazy as _

# import serapide_core.notifications_app
# import serapide_core.notifications_helper as notifications_helper
from serapide_core.notifications_helper import  NotificationsAppConfigBase


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

        # WARNING SOME MONKEY PATCHING HERE
        # import graphene_django
        # import graphene_django_extras
        # import logging
        # logging.getLogger(__name__).warning("MONKEY PATCHING convert_django_field_with_choices")
        # graphene_django.converter.convert_django_field_with_choices = graphene_django_extras.converter.convert_django_field_with_choices
        # graphene_django.types.convert_django_field_with_choices = graphene_django_extras.converter.convert_django_field_with_choices
