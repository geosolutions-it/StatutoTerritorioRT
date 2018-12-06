#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from .serializers import MembershipTypeSerializer, AppUserSerializer
from strt_users.models import Organization, MembershipType
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login


class UserAuthView(APIView):

    def post(self, request):
        user = authenticate(request.data)
        login(request, user)
        user_serializer = AppUserSerializer(user)
        return Response(user_serializer.data)

user_auth_view = UserAuthView.as_view()


class UserMembershipDataView(APIView):

    def get(self, request):
        selected_org = request.GET.get('selected_org')
        organizations_types = Organization.objects.\
            filter(pk=selected_org).values_list('type')
        m_types = MembershipType.objects.filter(
            organization_type__in=organizations_types
        )
        serialized_m_types = MembershipTypeSerializer(m_types, many=True)
        return Response(serialized_m_types.data)

userMembershipDataView = UserMembershipDataView.as_view()