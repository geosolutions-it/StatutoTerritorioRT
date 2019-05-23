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

from django import forms
from django.forms import ModelChoiceField
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (AppUser, Token,
                     Organization, OrganizationType,
                     UserMembership, MembershipType)
from django.utils.translation import gettext_lazy as _


@admin.register(Organization)
class OrganizationModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'type']
    search_fields = ['name', 'code', 'description', 'type']
    list_filter = ['name', 'code', 'description', 'type']


@admin.register(OrganizationType)
class OrganizationTypeModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code', 'description']
    list_filter = ['name', 'code', 'description']



class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.organization_type})"


class UserMembershipModelAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserMembershipModelAdminForm, self).__init__(*args, **kwargs)
        self.fields['type'] = MyModelChoiceField(queryset=self.fields['type'].queryset)


@admin.register(UserMembership)
class UserMembershipModelAdmin(admin.ModelAdmin):
    form = UserMembershipModelAdminForm
    list_display = ['name', 'description', 'member', 'organization', 'type']
    search_fields = ['name', 'description', 'member', 'organization', 'type']
    list_filter = ['name', 'description', 'member', 'organization', 'type']


@admin.register(MembershipType)
class MembershipTypeModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'organization_type']
    search_fields = ['name', 'code', 'description', 'organization_type']
    list_filter = ['name', 'code', 'description', 'organization_type']


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('fiscal_code', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('fiscal_code', 'password1', 'password2'),
        }),
    )
    list_display = ('fiscal_code', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('fiscal_code', 'first_name', 'last_name', 'email')
    ordering = ('fiscal_code',)


@admin.register(Token)
class TokenModelAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    search_fields = ['key', 'user', 'created']
    list_filter = ['key', 'user', 'created']
