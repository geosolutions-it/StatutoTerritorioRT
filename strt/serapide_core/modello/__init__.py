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
        ("message_sent", _("Messaggio Ricevuto"), _("Messaggio Ricevuto"),),
        ("piano_phase_changed", _("Piano Aggiornato"), _("Piano Aggiornato"),),
        ("contributi_tecnici", _("Contributi Tecnici"), _("Contributi Tecnici"),),
        ("piano_verifica_vas_updated", _("Documento Preliminare VAS"), _("Documento Preliminare VAS"),),
        ("conferenza_copianificazione", _("Conferenza di Copianificazione"), _("Conferenza di Copianificazione"),),
        ("tutti_pareri_inviati", _("Pareri pronti per la verifica"), _("Pareri pronti per la verifica"),),
        ("protocollo_genio_civile", _("Protocollo Genio Civile"), _("Protocollo Genio Civile"),),
        ("richiesta_integrazioni", _("Richiesta Integrazioni"), _("Richiesta Integrazioni"),),
        ("integrazioni_richieste", _("Integrazioni Richieste"), _("Integrazioni Richieste"),),
        ("trasmissione_adozione", _("Trasmissione Adozione"), _("Trasmissione Adozione"),),
        ("piano_controdedotto", _("Piano Controdedotto"), _("Piano Controdedotto"),),
        ("esito_conferenza_paesaggistica", _("Esito Conferenza Paesaggistica"), _("Esito Conferenza Paesaggistica"),),
        ("parere_motivato_ac", _("Parere Motivato AC"), _("Parere Motivato AC"),),
        ("upload_elaborati_adozione_vas", _("Elaborati Adozione VAS"), _("Elaborati Adozione VAS"),),
        ("rev_piano_post_cp", _("Revisione Piano post CP"), _("Revisione Piano post CP"),),
        ("trasmissione_approvazione", _("Trasmissione Approvazione"), _("Trasmissione Approvazione"),),
        ("attribuzione_conformita_pit", _("Attribuzione Conformità PIT"), _("Attribuzione Conformità PIT"),),
        ("pubblicazione_piano", _("Pubblicazione Piano"), _("Pubblicazione Piano"),),

        ("azione_generica", _("Nuova azione"), _("Nuova azione"),),
    )

    name = 'serapide_core.modello'

    def ready(self):
        super(SerapideCoreModelloAppConfig, self).ready()
        run_setup_hooks()


default_app_config = 'serapide_core.modello.SerapideCoreModelloAppConfig'
