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

from django.http import HttpResponseBadRequest
from django.contrib import auth

from strt_users.models import Token


class TokenMiddleware(object):
    """
    Middleware that authenticates against a token in the http authorization header.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        token = request.GET.get('token', None)

        if token is None:
            auth_header = request.META.get('HTTP_AUTHORIZATION', b'').split()
            if auth_header and auth_header[0].lower() == b'token':
                # If they specified an invalid token, let them know.
                if len(auth_header) != 2:
                    return HttpResponseBadRequest("Improperly formatted token")
                token = auth_header[1]

        if token:
            user = auth.authenticate(token=token)
            if user:
                request.user = request._cached_user = user
                auth.login(request, user)

        # ------------------------
        response = self.get_response(request)
        # ------------------------

        # Code to be executed for each request/response after
        # the view is called.

        return response
