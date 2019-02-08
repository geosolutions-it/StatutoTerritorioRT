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

from .notifications_helper import send_now_notification


def message_sent_notification(sender, **kwargs):
    if 'message' in kwargs:
        message = kwargs['message']
        thread = kwargs['thread']
        reply = kwargs['reply']
        users = list(thread.users.all())
        send_now_notification(users, "message_sent", {"from_user": message.sender})
