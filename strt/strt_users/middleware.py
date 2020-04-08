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
import logging

from django.conf import settings

from django.contrib import auth
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest, HttpResponseRedirect

from serapide_core.api.auth.user import (
    has_qualifica,
    is_soggetto_operante,
    can_access_piano,
    is_recognizable)
from strt_users.enums import Profilo, Qualifica
from strt_users.models import (
    Utente, Token,
    ProfiloUtente)
from serapide_core.modello.models import (
    Delega,
)


logger = logging.getLogger(__name__)


def assegna_token(delega: Delega, utente: Utente):

    logger.warning("Richiesta assegnazione Token [{}] a {}".format(delega.token, utente))

    piano = delega.delegante.piano
    ente = delega.delegante.qualifica_ufficio.ufficio.ente

    if has_qualifica(utente, ente, Qualifica.RESP):
        logger.warning("Assegnazione token rifiutata a responsabile")
        return False, "Assegnazione token rifiutata a responsabile"

    if is_soggetto_operante(utente, piano, delega.qualifica):
        logger.warning("Assegnazione token rifiutata a utente con qualifica già assegnata")
        return False, "Assegnazione token rifiutata a utente con qualifica già assegnata"

    token = delega.token
    token.user = utente
    token.save()

    if not ProfiloUtente.objects.filter(
            utente=utente,
            profilo=Profilo.OPERATORE).exists():
        p = ProfiloUtente(
            utente=utente,
            profilo=Profilo.OPERATORE,
            ente=ente
        )
        p.save()

    return True, None


class TokenMiddleware(object):
    """
    Middleware that authenticates against a token in the http authorization header.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.

        def create_redirect_piano(request, piano):
            return HttpResponseRedirect(
                '{request_path}/#/piano/{piano}/home'.format(
                    request_path=request.path,
                    piano=piano.codice))

        # Read token either from param or from header
        token = request.GET.get('token', None)
        if token is None:
            auth_header = request.META.get('HTTP_AUTHORIZATION', b'').split()
            if auth_header and auth_header[0].lower() == b'token':
                # If they specified an invalid token, let them know.
                if len(auth_header) != 2:
                    return HttpResponseBadRequest("Improperly formatted token")
                token = auth_header[1]

        if token:

            if not is_recognizable(request.user):
                logger.debug("Token specificato su utente sconosciuto")

                redirected = request.GET.get('redirected_by', None)
                if not redirected == 'TokenMiddleware':  # did we just redirect this
                    return HttpResponseRedirect(
                        '{login_path}?next={request_path}%3Ftoken={token}&redirected_by=TokenMiddleware'.format(
                            login_path=getattr(settings, 'LOGIN_URL', '/'),
                            request_path=request.path,
                            token=token))
            else:
                logger.debug("Token e utente specificati. Token [{}]".format(token))

                t: Token = Token.objects.filter(key=token).first()
                if t:
                    if not t.is_expired():
                        utente = request.user
                        d: Delega = Delega.objects.get(token=t)
                        piano = d.delegante.piano

                        if t.user is None:
                            ok, err = assegna_token(d, utente)
                            return create_redirect_piano(request, piano)

                        elif t.user == utente:
                            logger.info("Token già in uso [{}]".format(token))
                            return create_redirect_piano(request, piano)

                        else:
                            logger.warning("Token già assegnato ad altro utente [{}]".format(token))

                            # se l'utente ha cmq accesso al piano, usiamo il token come semplice bookmark
                            if can_access_piano(utente, piano):
                                return create_redirect_piano(request, piano)
                    else:
                        logger.warning("Token expired [{}]".format(token))
                else:
                    logger.warning("Token non trovato [{}]".format(token))

        # ------------------------
        # calls the view
        response = self.get_response(request)
        # ------------------------

        # Code to be executed for each request/response after the view is called.

        return response


# class TokenMiddleware__OLD(object):
#     """
#     Middleware that authenticates against a token in the http authorization header.
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         role = request.GET.get('role', None)
#         token = request.GET.get('token', None)
#         if token is None:
#             auth_header = request.META.get('HTTP_AUTHORIZATION', b'').split()
#             if auth_header and auth_header[0].lower() == b'token':
#                 # If they specified an invalid token, let them know.
#                 if len(auth_header) != 2:
#                     return HttpResponseBadRequest("Improperly formatted token")
#                 token = auth_header[1]
#
#         if token:
#             # user = auth.authenticate(token=token)
#             t = Token.objects.get(key=token)
#             d = Delega.objects.get(token=t)
#
#
#
#
#             if t and user:
#                 piano = t.delega.delegante.piano # ???
#                 request.user = request._cached_user = user
#                 organization = piano.ente
#                 request.session['ente'] = organization.code
#                 if not role:
#                     request.session['role'] = user.memberships.all().first().pk if user.memberships.all().first() \
#                     else None
#                 # TODO
#                 # attore = Contatto.attore(user, token=token)
#                 # request.session['attore'] = attore
#                 auth.login(request, user)
#
#         # ------------------------
#         response = self.get_response(request)
#         # ------------------------
#
#         # Code to be executed for each request/response after
#         # the view is called.
#
#         return response


class SessionControlMiddleware(object):
        """
        Middleware that checks if session variables have been correctly set.
        """
        def __init__(self, get_response):
            self.get_response = get_response
            # One-time configuration and initialization.

        def __call__(self, request):
            if not request.user.is_authenticated \
                    or not request.user.is_active \
                    or request.user.is_anonymous:

                redirect_to_login(request)
            # else:
            #     role = request.session['role'] if 'role' in request.session else None
            #     token = request.session['token'] if 'token' in request.session else None
            #     # TODO
            #     # if token:
            #     #     try:
            #     #         _t = Token.objects.get(key=token)
            #     #         if _t.is_expired():
            #     #             if not request.user.is_superuser:
            #     #                 return self.redirect_to_login(request)
            #     #     except BaseException:
            #     #         del request.session['token']
            #     #         traceback.print_exc()
            #
            #     ente = request.session.get('ente', None)
            #     if not ente:
            #         if not request.user.is_superuser:
            #             return self.redirect_to_login(request)
            #     else:
            #         try:
            #             Ente.objects.get(code=ente)
            #         except BaseException:
            #             traceback.print_exc()
            #             if not request.user.is_superuser:
            #                 return self.redirect_to_login(request)
            #
            #     attore = request.session['attore'] if 'attore' in request.session else None
            #     if not attore:
            #         # TODO
            #         return self.redirect_to_login(request)
            #
            #         # try:
            #         #     if token:
            #         #         attore = Contatto.attore(request.user, token=token)
            #         #     elif role:
            #         #         attore = Contatto.attore(request.user, role=role)
            #         #     elif organization:
            #         #         attore = Contatto.attore(request.user, organization=organization)
            #         #     request.session['attore'] = attore
            #         # except BaseException:
            #         #     traceback.print_exc()
            #         #
            #         # if not attore:
            #         #     if not request.user.is_superuser:
            #         #         return self.redirect_to_login(request)
            #     print(" ----------------------------- %s / %s " % (request.user, attore))
            # ------------------------
            response = self.get_response(request)
            # ------------------------

            # Code to be executed for each request/response after
            # the view is called.

            return response

def redirect_to_login(request):
    # if 'ente' in request.session:
    #     del request.session['ente']
    # if 'profilo' in request.session:
    #     del request.session['profilo']
    # if 'token' in request.session:
    #     del request.session['token']
    logout(request)
    redirect_to = getattr(settings, 'LOGOUT_REDIRECT_URL', reverse('user_registration'))
    return HttpResponseRedirect(
        '{login_path}?next={request_path}&redirected_by=SessionControlMiddleware'.format(
            login_path=redirect_to,
            request_path=request.path))
            # return HttpResponseRedirect('{login_path}'.format(login_path=redirect_to))
