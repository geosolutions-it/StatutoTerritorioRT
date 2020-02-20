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

from django.dispatch import Signal

from serapide_core.modello.models import SoggettoOperante
from strt_users.models import Assegnatario

from .notifications_helper import send_now_notification

# from serapide_core.modello.models import PianoAuthTokens

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


def piano_phase_changed_notification(sender, **kwargs):

    if 'piano' in kwargs:
        notification_type = kwargs['message_type']
        from_user = kwargs['user']
        piano = kwargs['piano']

        ufficio = []
        utenti = []
        tokens = []

        soqs = SoggettoOperante.objects.filter(piano=piano)
        qu_list = [so.qualifica_ufficio for so in soqs]

        ass_list = Assegnatario.objects.filter(qualifica_ufficio__in=qu_list)

        dest_uff = [{'nome':qu.ufficio.__str__(), 'email':qu.ufficio.email} for qu in qu_list ]
        dest_utenti = [{'nome':ass.utente.get_full_name(), 'email':ass.utente.email} for ass in ass_list ]
        # TODO tokens

        # if PianoAuthTokens.objects.filter(piano=piano).count() > 0:
        #     tokens = [_p.token for _p in PianoAuthTokens.objects.filter(piano=piano)]

        send_now_notification(dest_uff + dest_utenti,
                              notification_type,
                              {
                                "user": from_user,
                                "piano": piano,
                                "tokens": tokens
                              })
