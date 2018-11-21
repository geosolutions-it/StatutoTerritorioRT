#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.shortcuts import (
    render, redirect
)
from .forms import AppUserForm, UserMembershipForm
from .models import AppUser, UserMembership
from django_currentuser.middleware import (
    get_current_authenticated_user
)


def usersListView(request):
    current_user = get_current_authenticated_user()
    managed_users = AppUser.objects.filter(created_by=current_user)
    context = {
        'managed_users': managed_users
    }
    return render(request, 'strt_users/users_list.html', context)


def usersMembershipsListView(request):
    current_user = get_current_authenticated_user()
    managed_users = AppUser.objects.filter(created_by=current_user)
    managed_users_membership = UserMembership.objects.filter(member__in=managed_users)
    context = {
        'managed_users_membership': managed_users_membership
    }
    return render(request, 'strt_users/users_membership_list.html', context)


def userRegistrationView(request):
    if request.method == "POST":
        form = AppUserForm(request.POST)
        if form.is_valid():
            fiscal_code = form.cleaned_data['fiscal_code']
            # TODO: fiscal code verification by RT service (call endpoint), it could be done from client
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            AppUser.objects.create_user(
                fiscal_code=fiscal_code,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            return redirect('users_list')
    else:
        form = AppUserForm()
    context = {'form': form}
    return render(request, 'strt_users/user_registration.html', context)


def userMembershipRegistrationView(request):
    if request.method == "POST":
        form = UserMembershipForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            member = form.cleaned_data['member']
            organization = form.cleaned_data['organization']
            type = form.cleaned_data['type']
            UserMembership.objects.create(
                description=description,
                member=member,
                organization=organization,
                type=type
            )
            return redirect('users_membership_list')
    else:
        form = UserMembershipForm()
        current_user = get_current_authenticated_user()
        form.fields['member'].queryset = AppUser.objects.filter(created_by=current_user)
        # Membership_type must be filtered considering the selected organization type
    context = {'form': form}
    return render(request, 'strt_users/user_membership_registration.html', context)


def userMembershipDeleteView(request, code):
    UserMembership.objects.filter(code=code).delete()
    return redirect('users_membership_list')


def userDeleteView(request, fiscal_code):
    AppUser.objects.filter(fiscal_code=fiscal_code).delete()
    return redirect('users_list')

























