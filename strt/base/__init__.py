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

from __future__ import absolute_import, unicode_literals
from .celery_app import app as celery_app

default_app_config = "base.apps.BaseConfig"

__all__ = ('celery_app',)
