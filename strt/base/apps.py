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

from django.apps import AppConfig


def run_setup_hooks(*args, **kwargs):
    from django.conf import settings
    from .celery_app import app as celery_app
    if celery_app not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += (celery_app, )


class BaseConfig(AppConfig):
    name = 'base'

    def ready(self):
        super(BaseConfig, self).ready()
        run_setup_hooks()
