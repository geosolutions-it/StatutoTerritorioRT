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

from django.apps import AppConfig


# signals management
def model_object_post_save(instance, *args, **kwargs):
    instance.post_save()


def run_setup_hooks(*args, **kwargs):
    from django.db.models import signals

    from .models import Piano

    signals.post_save.connect(model_object_post_save, sender=Piano)


class SerapideCoreModelloAppConfig(AppConfig):
    name = 'serapide_core.modello'

    def ready(self):
        super(SerapideCoreModelloAppConfig, self).ready()
        run_setup_hooks()


default_app_config = 'serapide_core.modello.SerapideCoreModelloAppConfig'
