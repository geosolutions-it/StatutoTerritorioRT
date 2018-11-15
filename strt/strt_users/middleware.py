#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from .utils import set_current_user


class CurrentUserMiddleware:

    def process_request(self, request):
        set_current_user(getattr(request, 'user', None))