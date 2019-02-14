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

from pkgutil import extend_path


__path__ = extend_path(__path__, __name__)  # noqa

default_app_config = "strt_tests.apps.StrtPortalTestConfig"
