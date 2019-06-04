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

from django.conf import settings
from django.db.models import Q
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


def get_managed_users(current_user, current_role, organization, organizazions_enabled, full=False):
    managed_users = AppUser.objects.filter(
        Q(usermembership__organization__in=organizazions_enabled) |
        Q(created_by=current_user))
    managed_roles = []
    if current_role.code == settings.RESPONSABILE_ISIDE_CODE and not full:
        managed_roles = [settings.RUP_CODE]
        managed_users = managed_users.filter(
            Q(usermembership__type__code__in=managed_roles)).exclude(
                pk__in=[current_user.pk, ]).distinct()
    elif current_role.code == settings.RUP_CODE or full:
        managed_users = managed_users.exclude(pk__in=[current_user.pk, ]).distinct()

    return managed_users

@login_required
def userProfileDetailView(request):
    current_user = get_current_authenticated_user()
    current_user_memberships = UserMembership.objects.filter(
        member=current_user).exclude(type__code__in=[settings.TEMP_USER_CODE])
    managed_users = AppUser.objects.filter(created_by=current_user)
    managed_users_memberships = UserMembership.objects.filter(
        member__in=managed_users).exclude(type__code__in=[settings.TEMP_USER_CODE])
    context = {
        'current_user': current_user,
        'current_user_memberships': current_user_memberships,
        'managed_users': managed_users,
        'managed_users_memberships': managed_users_memberships
    }
    return render(request, 'strt_users/user_profile_detail.html', context)


@permission_required('strt_users.can_manage_users')
def usersListView(request):
    managed_users = []
    if 'organization' in request.session and request.session['organization']:
        current_user = get_current_authenticated_user()
        organization = request.session['organization']
        organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
        current_role = current_user.memberships.filter(organization=organization).first().type
        managed_users = get_managed_users(current_user, current_role, organization, organizazions_enabled)
    context = {
        'managed_users': managed_users
    }
    return render(request, 'strt_users/users_list.html', context)


@permission_required('strt_users.can_manage_users')
def usersMembershipsListView(request):
    managed_users = []
    if 'organization' in request.session and request.session['organization']:
        current_user = get_current_authenticated_user()
        organization = request.session['organization']
        organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
        current_role = current_user.memberships.filter(organization=organization).first().type
        managed_users = get_managed_users(current_user, current_role, organization, organizazions_enabled)
        managed_users_membership = UserMembership.objects.filter(
            member__in=managed_users).exclude(type__code__in=[settings.TEMP_USER_CODE])
    context = {
        'managed_users_membership': managed_users_membership
    }
    return render(request, 'strt_users/users_membership_list.html', context)


@permission_required('strt_users.can_manage_users')
def userRegistrationView(request):
    if request.method == "POST":
        form = AppUserForm(request.POST)
        if 'organization' in request.session and request.session['organization']:
            current_user = get_current_authenticated_user()
            organization = request.session['organization']
            organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
            current_role = current_user.memberships.filter(organization=organization).first().type
            if form.is_valid():
                fiscal_code = form.cleaned_data['fiscal_code']
                email = form.cleaned_data['email']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                name = 'TMP_%s' % fiscal_code

                new_user = AppUser.objects.create_user(
                    fiscal_code=fiscal_code.upper(),
                    email=email,
                    first_name=first_name.title(),
                    last_name=last_name.title(),
                    is_active=False
                )
                new_role = MembershipType.objects.get(
                    code=settings.READ_ONLY_USER_CODE,
                    organization_type=current_role.organization_type)
                UserMembership.objects.create(
                    name=name,
                    description=name,
                    member=new_user,
                    organization=Organization.objects.get(code=organization),
                    type=new_role,
                    created_by=current_user
                )

                return redirect('users_list')
    else:
        managed_users = []
        if 'organization' in request.session and request.session['organization']:
            current_user = get_current_authenticated_user()
            organization = request.session['organization']
            organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
            current_role = current_user.memberships.filter(organization=organization).first().type
            managed_users = get_managed_users(current_user, current_role, organization, organizazions_enabled)
        form = AppUserForm()
        form.fields[AppUser.USERNAME_FIELD].queryset = AppUser.objects.filter(pk__in=managed_users)
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
            attore = form.cleaned_data['attore']
            name = '{}_{}_{}'.format(attore, type, organization).upper()
            role, created = UserMembership.objects.get_or_create(
                name='TMP_%s' % member.fiscal_code)
            role.name = name
            role.description = description or '{} - {} {}'.format(str(attore).upper(), type, organization)
            role.member = member
            role.organization = organization
            role.type = type
            role.attore = attore
            role.save()

            return redirect('users_membership_list')
    else:
        form = UserMembershipForm()
        managed_users = []
        if 'organization' in request.session and request.session['organization']:
            current_user = get_current_authenticated_user()
            organization = request.session['organization']
            organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
            current_role = current_user.memberships.filter(organization=organization).first().type
            managed_users = get_managed_users(current_user, current_role, organization, organizazions_enabled, full=True)
            managed_roles = []
            if current_role.code == settings.RESPONSABILE_ISIDE_CODE:
                managed_roles = [settings.RUP_CODE]
            elif current_role.code == settings.RUP_CODE:
                managed_roles = [settings.READ_ONLY_USER_CODE,
                                 # settings.TEMP_USER_CODE,
                                 settings.OPERATOR_USER_CODE]
            form.fields['member'].queryset = AppUser.objects.filter(pk__in=managed_users)
            form.fields['organization'].queryset = Organization.objects.filter(pk__in=organizazions_enabled)
            form.fields['type'].queryset = MembershipType.objects.filter(
                code__in=managed_roles,
                organization_type=current_role.organization_type)
        else:
            form.fields['member'].widget.attrs['disabled'] = True
            form.fields['organization'].widget.attrs['disabled'] = True
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
        managed_users = []
        if 'organization' in request.session and request.session['organization']:
            current_user = get_current_authenticated_user()
            organization = request.session['organization']
            organizazions_enabled = UserMembership.objects.filter(member=current_user).values_list('organization')
            current_role = current_user.memberships.filter(organization=organization).first().type
            managed_users = get_managed_users(current_user, current_role, organization, organizazions_enabled, full=True)
            managed_roles = []
            if current_role.code == settings.RESPONSABILE_ISIDE_CODE:
                managed_roles = [settings.RUP_CODE]
            elif current_role.code == settings.RUP_CODE:
                managed_roles = [settings.READ_ONLY_USER_CODE,
                                 # settings.TEMP_USER_CODE,
                                 settings.OPERATOR_USER_CODE]
            form.fields['member'].queryset = AppUser.objects.filter(pk__in=managed_users)
            form.fields['organization'].queryset = Organization.objects.filter(pk__in=organizazions_enabled)
            form.fields['type'].queryset = MembershipType.objects.filter(
                code__in=managed_roles,
                organization_type=current_role.organization_type)
        else:
            form.fields['member'].widget.attrs['disabled'] = True
            form.fields['organization'].widget.attrs['disabled'] = True
            form.fields['type'].widget.attrs['disabled'] = True
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
    member = UserMembership.objects.get(code=code).member
    if UserMembership.objects.filter(member=member).count() > 1:
        UserMembership.objects.filter(code=code).delete()
    return redirect('users_membership_list')


@permission_required('strt_users.can_manage_users')
def userDeleteView(request, fiscal_code):
    AppUser.objects.filter(fiscal_code=fiscal_code.upper()).delete()
    return redirect('users_list')
