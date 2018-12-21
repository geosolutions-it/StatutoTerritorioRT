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

class DjangoSerapideBaseException(Exception):
    """Base class for exceptions in this module."""
    pass


default_app_config = "serapide_core.apps.AppConfig"
