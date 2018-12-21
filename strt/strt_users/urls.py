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

from django.urls import path, include
from .views import (
    userMembershipRegistrationView, usersMembershipsListView,
    userMembershipDeleteView, userRegistrationView, usersListView,
    userDeleteView, userUpdateView, userMembershipUpdateView,
    userProfileDetailView
)
from api.views import user_membership_data_view


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('membership-type-api/', user_membership_data_view, name='membership_type_data'),
    path('user-profile/', userProfileDetailView, name='users_profile_detail'),
    path('users-list/', usersListView, name='users_list'),
    path('user-registration/', userRegistrationView, name='user_registration'),
    path('user-update/<fiscal_code>', userUpdateView, name='user_update'),
    path('user-delete/<fiscal_code>/', userDeleteView, name='user_delete'),
    path('users-membership-list/', usersMembershipsListView, name='users_membership_list'),
    path('user-membership-registration/', userMembershipRegistrationView, name='user_membership_registration'),
    path('user-membership-delete/<code>/', userMembershipDeleteView, name='user_membership_delete'),
    path('user-membership-update/<code>/', userMembershipUpdateView, name='user_membership_update'),
]
