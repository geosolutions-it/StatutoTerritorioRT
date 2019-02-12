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

from django.dispatch import Signal

from .notifications_helper import send_now_notification


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
        from_user = kwargs['user']
        piano = kwargs['piano']

        users = []
        
