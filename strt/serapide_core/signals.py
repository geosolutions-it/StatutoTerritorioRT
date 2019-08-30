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

import logging

from django.dispatch import Signal

from .notifications_helper import send_now_notification

from serapide_core.modello.models import PianoAuthTokens

logger = logging.getLogger(__name__)

# ############################################################################ #
# Signals
# ############################################################################ #
"""
e.g:
    message_sent = Signal(providing_args=["message", "thread", "reply"])
    ...
    message_sent.send(sender=cls, message=msg, thread=thread, reply=True)
"""
piano_phase_changed = Signal(providing_args=["user", "piano", ])


# ############################################################################ #
# Signal Handlers
# ############################################################################ #
def message_sent_notification(sender, **kwargs):

    if 'message' in kwargs:
        message = kwargs['message']
        thread = kwargs['thread']
        reply = kwargs['reply']
        users = [u for u in thread.users.all() if u != message.sender]

        send_now_notification(users,
                              "message_sent",
                              {
                                "from_user": message.sender,
                                "message": message,
                                "thread": thread,
                                "reply": reply
                              })


def log(piano, notification_type, user_type, user):
    logger.info("SEND {piano}:{azione} TO {usertype} {user}".format(
        user=user,
        usertype=user_type,
        piano=piano.codice,
        azione=notification_type))

def piano_phase_changed_notification(sender, **kwargs):

    logger.info("========== piano_phase_changed_notification")
    #logger.warning(kwargs, stack_info=True)

    if 'piano' in kwargs:
        notification_type = kwargs['message_type']
        from_user = kwargs['user']
        piano = kwargs['piano']

        users = []
        tokens = []
        if piano.soggetto_proponente:
            users.append(piano.soggetto_proponente.user)
            log(piano, notification_type, "proponente", piano.soggetto_proponente.user)

        if piano.autorita_competente_vas:
            for _c in piano.autorita_competente_vas.all():
                users.append(_c.user)
                log(piano, notification_type, "autorita_competente_vas", _c.user)

        if piano.autorita_istituzionali:
            for _c in piano.autorita_istituzionali.all():
                users.append(_c.user)
                log(piano, notification_type, "autorita_istituzionali", _c.user)

        if piano.altri_destinatari:
            for _c in piano.altri_destinatari.all():
                users.append(_c.user)
                log(piano, notification_type, "altri_destinatari", _c.user)

        if piano.soggetti_sca:
            for _c in piano.soggetti_sca.all():
                users.append(_c.user)
                log(piano, notification_type, "soggetti_sca", _c.user)

        if PianoAuthTokens.objects.filter(piano=piano).count() > 0:
            tokens = [_p.token for _p in PianoAuthTokens.objects.filter(piano=piano)]

        send_now_notification(users,
                              notification_type,
                              {
                                  "user": from_user,
                                  "piano": piano,
                                  "tokens": tokens
                              })
