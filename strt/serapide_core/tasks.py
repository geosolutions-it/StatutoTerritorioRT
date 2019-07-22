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


@shared_task
def synch_actions(*args):
    """TODO

    """
    import datetime

    from django.conf import settings
    from django.utils import timezone

    from serapide_core.modello.enums import (
        FASE, STATO_AZIONE)
    from serapide_core.modello.models import Piano

    _piani = Piano.objects.all().exclude(fase=FASE.pubblicazione)

    for _piano in _piani:
        logger.info(" -------------------------------------- PIANO: %s " % _piano.codice)
        _azioni = _piano.azioni.filter(stato=STATO_AZIONE.attesa)
        for _azione in _azioni:
            _now = datetime.datetime.now(timezone.get_current_timezone())
            logger.info(" -------------------------------------- NOW: %s " % _now)
            if _azione.data and _now >= _azione.data:
                logger.info(" -------------------------------------- AZIONE: %s / %s " % (_azione.tipologia, _azione.data))
                _azione.stato = STATO_AZIONE.nessuna
                _azione.data = _now
                _azione.save()
