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

import traceback
from django.conf import settings

from django.contrib import auth
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest, HttpResponseRedirect

from strt_users.models import Token, Organization
from serapide_core.modello.models import PianoAuthTokens, Contatto


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
        role = request.GET.get('role', None)
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
            _allowed_pianos = [_pt.piano for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            if user and _allowed_pianos and len(_allowed_pianos) > 0:
                request.user = request._cached_user = user
                organization = _allowed_pianos[0].ente
                request.session['organization'] = organization.code
                if not role:
                    request.session['role'] = user.memberships.all().first().pk if user.memberships.all().first() \
                    else None
                attore = Contatto.attore(user, token=token)
                request.session['attore'] = attore
                auth.login(request, user)

        # ------------------------
        response = self.get_response(request)
        # ------------------------

        # Code to be executed for each request/response after
        # the view is called.

        return response


class SessionControlMiddleware(object):
        """
        Middleware that checks if session variables have been correctly set.
        """
        def __init__(self, get_response):
            self.get_response = get_response
            # One-time configuration and initialization.

        def __call__(self, request):
            if not request.user.is_authenticated or \
            not request.user.is_active or \
            request.user.is_anonymous:
                self.redirect_to_login(request)
            else:
                role = request.session['role'] if 'role' in request.session else None
                token = request.session['token'] if 'token' in request.session else None
                if token:
                    try:
                        _t = Token.objects.get(key=token)
                        if _t.is_expired():
                            if not request.user.is_superuser:
                                return self.redirect_to_login(request)
                    except BaseException:
                        del request.session['token']
                        traceback.print_exc()

                organization = request.session['organization'] if 'organization' in request.session else None
                if not organization:
                    if not request.user.is_superuser:
                        return self.redirect_to_login(request)
                else:
                    try:
                        Organization.objects.get(code=organization)
                    except BaseException:
                        traceback.print_exc()
                        if not request.user.is_superuser:
                            return self.redirect_to_login(request)

                attore = request.session['attore'] if 'attore' in request.session else None
                if not attore:
                    try:
                        if token:
                            attore = Contatto.attore(request.user, token=token)
                        elif role:
                            attore = Contatto.attore(request.user, role=role)
                        elif organization:
                            attore = Contatto.attore(request.user, organization=organization)
                        request.session['attore'] = attore
                    except BaseException:
                        traceback.print_exc()

                    if not attore:
                        if not request.user.is_superuser:
                            return self.redirect_to_login(request)
            # ------------------------
            response = self.get_response(request)
            # ------------------------

            # Code to be executed for each request/response after
            # the view is called.

            return response

        def redirect_to_login(self, request):
            if 'organization' in request.session:
                del request.session['organization']
            if 'attore' in request.session:
                del request.session['attore']
            if 'token' in request.session:
                del request.session['token']
            logout(request)
            redirect_to = getattr(settings, 'LOGOUT_REDIRECT_URL', reverse('user_registration'))
            return HttpResponseRedirect(
                '{login_path}?next={request_path}'.format(
                    login_path=redirect_to,
                    request_path=request.path))
            return HttpResponseRedirect('{login_path}'.format(login_path=redirect_to))
