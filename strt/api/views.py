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

# from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from strt_users.models import (
    Organization,
    # MembershipType
)

from .serializers import (
    # MembershipTypeSerializer,
    UserMembershipSerializer,
)

UserModel = get_user_model()


class UserMembershipDataView(APIView):

    def get(self, request):
        user_id = request.GET.get('user_id')
        selected_org = request.GET.get('selected_org')

        if not user_id or not selected_org:
            return Response({})

        user = UserModel._default_manager.filter(
            fiscal_code=user_id.strip().upper()
        ).first()

        organization = Organization.objects.filter(
            code=selected_org
        ).first()

        if user and organization:
            # organizations_types = Organization.objects.\
            #     filter(pk=selected_org).values_list('type')
            # m_types = MembershipType.objects.filter(
            #     organization_type__in=organizations_types
            # ).exclude(code=settings.RESPONSABILE_ISIDE_CODE).exclude(code=settings.RUP_CODE)
            m_types = user.memberships.filter(organization=organization)
            # serialized_m_types = MembershipTypeSerializer(m_types, many=True)
            serialized_m_types = UserMembershipSerializer(m_types, many=True)
            return Response(serialized_m_types.data)

        return Response({})


user_membership_data_view = UserMembershipDataView.as_view()
