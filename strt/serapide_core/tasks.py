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

from django.conf import settings

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def send_queued_notifications(self, *args):
    """Sends queued notifications.

    settings.PINAX_NOTIFICATIONS_QUEUE_ALL needs to be true in order to take
    advantage of this.

    """

    try:
        from notification.engine import send_all
    except ImportError:
        return

    # Make sure application can write to location where lock files are stored
    if not args and getattr(settings, 'NOTIFICATION_LOCK_LOCATION', None):
        send_all(settings.NOTIFICATION_LOCK_LOCATION)
    else:
        send_all(*args)
