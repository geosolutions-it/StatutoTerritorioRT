#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from .serializers import MembershipTypeSerializer
from strt_users.models import Organization, MembershipType
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


class UserMembershipDataView(APIView):

    def get(self, request):
        selected_org = request.GET.get('selected_org')
        organizations_types = Organization.objects.\
            filter(pk=selected_org).values_list('type')
        m_types = MembershipType.objects.filter(
            organization_type__in=organizations_types
        ).exclude(code=settings.RESPONSABILE_ISIDE_CODE)
        serialized_m_types = MembershipTypeSerializer(m_types, many=True)
        return Response(serialized_m_types.data)

user_membership_data_view = UserMembershipDataView.as_view()