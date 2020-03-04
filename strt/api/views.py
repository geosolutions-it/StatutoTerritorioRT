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

import logging
import json

from django.conf import settings
from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.response import Response

from serapide_core.schema import schema

from strt_users.models import (
    Utente,
    Ente,
    # MembershipType
)
from serapide_core.tests.test_data_setup import DataLoader

from .serializers import (
    ProfiloSerializer,
    QualificaSerializer,
)

UserModel = get_user_model()

logger = logging.getLogger(__name__)

class UserMembershipDataView(APIView):

    def get(self, request):
        # DataLoader.loadData()
        # usando SPID, dovremo avere tutti le informazioni dell'utente negli header
        # - controllare se esiste l'utente in locale tramite CF
        # - eventualmente aggiungere l'utente nel db LOCALE

        # senza SPID siamo in condizioni di test, e prendiamo semplicemente il CF dalla request


        user = get_user(request)

        if isinstance(user, AnonymousUser):
            logger.warning('SESSION NOT BOUND TO ANY USER. Using passed in params for debug call')
            user_id = request.GET.get('user_id')

            if not user_id:
                return Response(status=401, data='Unauthorized')

            logger.warning("USER ID : " + user_id)

            user = UserModel._default_manager.\
                filter(fiscal_code=user_id.strip().upper()).\
                first()

        # u = Utente.objects.filter(fiscal_code=user_id.strip().upper()).first()
        #
        # logger.warning("USER : " + u)

        if not user or isinstance(user, AnonymousUser):
            return Response(status=401, data='Unauthorized')
            # return Response(status=404, data='User not found')

        result = query("""
    query {
        userChoices(fiscalCode: "{cf}") {
            edges {
                node {
                    fiscalCode
                    firstName
                    lastName

                    profili {
                        profilo
                        ente       { ipa nome}
                        qualifiche { qualifica ufficio}
                    }
                }
            }                         
        }
    }""".replace('{cf}', user.fiscal_code), request)

        return Response(result.data)

        # return Response({})

def query(q, request):
    result = schema.execute(q, context=request)
    if result.errors:
        logger.warning("ERRORS:::::::::::::::::::")
        for error in result.errors:
            logger.warning(error);
    else:
        logger.warning("RESULT::::::::::::::::::")
        logger.warning(result)
        logger.warning("RESULT DATA::::::::::::::::::.")
        try:
            logger.warning(json.dumps(result.data, indent=4))
        except:
            logger.warning(result.data)
    logger.warning("-------------------------")
    return result

user_membership_data_view = UserMembershipDataView.as_view()
