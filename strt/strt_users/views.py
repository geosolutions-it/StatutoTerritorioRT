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

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from .forms import AppUserForm, UserMembershipForm
from .models import (
    AppUser, UserMembership, Organization, MembershipType
)
from django_currentuser.middleware import (
    get_current_authenticated_user
)
from django.contrib.auth.decorators import login_required
from rules.contrib.views import permission_required


@login_required
def userProfileDetailView(request):
    current_user = get_current_authenticated_user()
    current_user_memberships = UserMembership.objects.filter(member=current_user)
    managed_users = AppUser.objects.filter(created_by=current_user)
    managed_users_memberships = UserMembership.objects.filter(member__in=managed_users)
    context = {
        'current_user': current_user,
        'current_user_memberships': current_user_memberships,
        'managed_users': managed_users,
        'managed_users_memberships': managed_users_memberships
    }
    return render(request, 'strt_users/user_profile_detail.html', context)


@permission_required('strt_users.can_manage_users')
def usersListView(request):
    current_user = get_current_authenticated_user()
    managed_users = AppUser.objects.filter(created_by=current_user)
    context = {
        'managed_users': managed_users
    }
    return render(request, 'strt_users/users_list.html', context)


@permission_required('strt_users.can_manage_users')
def usersMembershipsListView(request):
    current_user = get_current_authenticated_user()
    managed_users = AppUser.objects.filter(created_by=current_user)
    managed_users_membership = UserMembership.objects.filter(member__in=managed_users)
    context = {
        'managed_users_membership': managed_users_membership
    }
    return render(request, 'strt_users/users_membership_list.html', context)


@permission_required('strt_users.can_manage_users')
def userRegistrationView(request):
    if request.method == "POST":
        form = AppUserForm(request.POST)
        if form.is_valid():
            fiscal_code = form.cleaned_data['fiscal_code']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            AppUser.objects.create_user(
                fiscal_code=fiscal_code.upper(),
                email=email,
                first_name=first_name.title(),
                last_name=last_name.title(),
                is_active=False
            )
            return redirect('users_list')
    else:
        form = AppUserForm()
    context = {'form': form}
    return render(request, 'strt_users/user_registration.html', context)


@permission_required('strt_users.can_manage_users')
def userMembershipRegistrationView(request):
    if request.method == "POST":
        form = UserMembershipForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            member = form.cleaned_data['member']
            organization = form.cleaned_data['organization']
            type = form.cleaned_data['type']
            UserMembership.objects.create(
                name=f'{type} {organization}',  # noqa
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
        organizations = UserMembership.objects.filter(member=current_user).values_list('organization')
        form.fields['organization'].queryset = Organization.objects.filter(pk__in=organizations)
        form.fields['type'].widget.attrs['disabled'] = True
    context = {'form': form}
    return render(request, 'strt_users/user_membership_registration.html', context)


@permission_required('strt_users.can_manage_users')
def userMembershipUpdateView(request, code):
    instance = get_object_or_404(UserMembership, code=code)
    if request.method == "POST":
        form = UserMembershipForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('users_membership_list')
    else:
        form = UserMembershipForm(instance=instance)
        current_user = get_current_authenticated_user()
        form.fields['member'].queryset = AppUser.objects.filter(created_by=current_user)
        organizations = UserMembership.objects.filter(member=current_user).values_list('organization')
        form.fields['organization'].queryset = Organization.objects.filter(pk__in=organizations)
        organizations_types = Organization.objects.filter(pk=instance.organization.code).values_list('type')
        form.fields['type'].queryset = MembershipType.objects.filter(
            organization_type__in=organizations_types
        )
    context = {
        'form': form,
        'action': 'update'
    }
    return render(request, 'strt_users/user_membership_registration.html', context)


@permission_required('strt_users.can_manage_users')
def userUpdateView(request, fiscal_code):
    instance = get_object_or_404(AppUser, fiscal_code=fiscal_code.upper())
    form = AppUserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('users_list')
    return render(request,
                  'strt_users/user_registration.html',
                  {
                      'form': form,
                      'action': 'update'
                  })


@permission_required('strt_users.can_manage_users')
def userMembershipDeleteView(request, code):
    UserMembership.objects.filter(code=code).delete()
    return redirect('users_membership_list')


@permission_required('strt_users.can_manage_users')
def userDeleteView(request, fiscal_code):
    AppUser.objects.filter(fiscal_code=fiscal_code.upper()).delete()
    return redirect('users_list')
