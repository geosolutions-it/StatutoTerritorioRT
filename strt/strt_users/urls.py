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
    userMembershipRegistrationView, usersMembershipsListView, userMembershipDeleteView,
    userRegistrationView, usersListView, userDeleteView
)


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('users-list/', usersListView, name='users_list'),
    path('user-registration/', userRegistrationView, name='user_registration'),
    path('user-delete/<fiscal_code>/', userDeleteView, name='user_delete'),
    path('users-membership-list/', usersMembershipsListView, name='users_membership_list'),
    path('user-membership-registration/', userMembershipRegistrationView, name='user_membership_registration'),
    path('user-membership-delete/<code>/', userMembershipDeleteView, name='user_membership_delete'),
]
