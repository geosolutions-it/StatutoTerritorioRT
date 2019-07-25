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
    import imp
    import inspect
    import datetime
    import importlib

    from django.utils import timezone
    from serapide_core.modello.enums import (
        FASE, STATO_AZIONE)
    from serapide_core.modello.models import Piano

    def fullname(o):
        # o.__module__ + "." + o.__class__.__qualname__ is an example in
        # this context of H.L. Mencken's "neat, plausible, and wrong."
        # Python makes no guarantees as to whether the __module__ special
        # attribute is defined, so we take a more circumspect approach.
        # Alas, the module name is explicitly excluded from __qualname__
        # in Python 3.
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__  # Avoid reporting __builtin__
        else:
            return module + '.' + o.__class__.__name__

    def import_from_dotted_path(dotted_names, path=None):
        """ import_from_dotted_path('foo.bar') -> from foo import bar; return bar """
        next_module, remaining_names = dotted_names.split('.', 1)
        fp, pathname, description = imp.find_module(next_module, path)
        module = imp.load_module(next_module, fp, pathname, description)
        if hasattr(module, remaining_names):
            return getattr(module, remaining_names)
        if '.' not in remaining_names:
            return module
        return import_from_dotted_path(remaining_names, path=module.__path__)

    _piani = Piano.objects.all().exclude(fase=FASE.pubblicazione)

    for _piano in _piani:
        logger.info(" -------------------------------------- PIANO: %s / %s " % (_piano.codice, _piano.next_phase))
        _azioni = _piano.azioni.filter(stato=STATO_AZIONE.attesa)
        for _azione in _azioni:
            _now = datetime.datetime.now(timezone.get_current_timezone())
            if _azione.data and _now >= _azione.data:
                _module = 'serapide_core.api.graphene.mutations.' + _piano.next_phase.strip()
                mutations = importlib.import_module(_module)
                for _c in dir(mutations):
                    obj = import_from_dotted_path('.'.join([mutations.__name__, _c]))
                    if inspect.isclass(obj) and getattr(obj, 'action', None):
                        if _azione.tipologia == obj.action():
                            logger.info(" -------------------------------------- AZIONE: %s / %s " % (_azione.tipologia, _azione.data))
                            logger.info(" -------------------------------------- PACKAGE: %s " % fullname(_azione))
                            obj.update_actions_for_phase(_piano.fase, _piano, obj.procedura(_piano), None)
