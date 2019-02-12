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

    # 1. message_sent
    from pinax.messages.signals import message_sent
    from .signals import message_sent_notification
    message_sent.connect(message_sent_notification)

    # 2. piano_phase_changed
    from .signals import piano_phase_changed, piano_phase_changed_notification
    piano_phase_changed.connect(piano_phase_changed_notification)


class AppConfig(NotificationsAppConfigBase):

    name = "serapide_core"
    label = "serapide_core"
    verbose_name = _("Django SERAPIDE - Core")

    NOTIFICATIONS = (
        ("message_sent", _("Messaggio Inviato"), _("Messaggio Inviato"),),
        ("piano_phase_changed", _("Piano Aggiornato"), _("Piano Aggiornato"),),
    )

    def ready(self):
        """Connect relevant signals to their corresponding handlers"""
        super(AppConfig, self).ready()
        run_setup_hooks()
