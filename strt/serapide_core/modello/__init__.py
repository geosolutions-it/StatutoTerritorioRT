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

from ..notifications_helper import NotificationsAppConfigBase


# signals management
def model_object_post_save(instance, *args, **kwargs):
    instance.post_save()


def run_setup_hooks(*args, **kwargs):
    # 0. Model Signals
    from django.db.models import signals
    from .models import Piano
    import serapide_core.signals as core_signals

    signals.post_save.connect(model_object_post_save, sender=Piano)

    # 1. message_sent
    from pinax.messages.signals import message_sent
    message_sent.connect(core_signals.message_sent_notification)

    # 2. piano_phase_changed
    core_signals.piano_phase_changed.connect(
        core_signals.piano_phase_changed_notification)


class SerapideCoreModelloAppConfig(NotificationsAppConfigBase):

    NOTIFICATIONS = (
        # label, display, description
        # ("message_sent", _("Messaggio Ricevuto"), _("Messaggio Ricevuto"),),
        ("piano_phase_changed", _("Piano Aggiornato"), _("Piano Aggiornato"),),
        ("pubblicazione_piano", _("Pubblicazione Piano"), _("Pubblicazione Piano"),),

        ("azione_generica", _("Nuova azione"), _("Nuova azione"),),
        ("azione_creato_piano", "Nuovo piano creato", "Nuovo piano creato",),
    )

    name = 'serapide_core.modello'

    def ready(self):
        super(SerapideCoreModelloAppConfig, self).ready()
        run_setup_hooks()


default_app_config = 'serapide_core.modello.SerapideCoreModelloAppConfig'
