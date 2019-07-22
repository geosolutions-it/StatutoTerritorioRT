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


def _log(msg, *args):
    logger.info(msg, *args)


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

""" CELERAY SAMPLE TASKS
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

@app.task
def test(arg):
    _log(arg)

@app.task(bind=True)
def debug_task(self):
    _log("Request: {!r}".format(self.request))
"""
