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

from ..notifications_helper import NotificationsAppConfigBase


# signals management
def model_object_post_save(instance, *args, **kwargs):
    instance.post_save()


def run_setup_hooks(*args, **kwargs):
    # 0. Model Signals
    from django.db.models import signals
    from .models import Piano
    signals.post_save.connect(model_object_post_save, sender=Piano)

    # 1. message_sent
    from pinax.messages.signals import message_sent
    from ..signals import message_sent_notification
    message_sent.connect(message_sent_notification)

    # 2. piano_phase_changed
    from ..signals import piano_phase_changed, piano_phase_changed_notification
    piano_phase_changed.connect(piano_phase_changed_notification)


class SerapideCoreModelloAppConfig(NotificationsAppConfigBase):

    NOTIFICATIONS = (
        # label, display, description
        ("message_sent", _("Messaggio Ricevuto"), _("Messaggio Ricevuto"),),
        ("piano_phase_changed", _("Piano Aggiornato"), _("Piano Aggiornato"),),
        ("piano_verifica_vas_updated", _("Documento Preliminare VAS"), _("Documento Preliminare VAS"),),
        ("conferenza_copianificazione", _("Conferenza di Copianificazione"), _("Conferenza di Copianificazione"),),
        ("tutti_pareri_inviati", _("Pareri pronti per la verifica"), _("Pareri pronti per la verifica"),),
        ("protocollo_genio_civile", _("Protocollo Genio Civile"), _("Protocollo Genio Civile"),),
    )

    name = 'serapide_core.modello'

    def ready(self):
        super(SerapideCoreModelloAppConfig, self).ready()
        run_setup_hooks()


default_app_config = 'serapide_core.modello.SerapideCoreModelloAppConfig'
