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

from __future__ import absolute_import

import os
import logging

from celery import Celery
# from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings.settings')

app = Celery('base')
logger = logging.getLogger(__name__)

logger.warning("*** CREATING CELERY APP")



# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))