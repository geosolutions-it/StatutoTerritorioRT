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
from .models import (Utente, Ente, Ufficio, QualificaUfficio, Assegnatario, Token)
from django.utils.translation import gettext_lazy as _


@admin.register(Ente)
class EnteModelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id', 'descrizione']
    search_fields = ['nome', 'id', 'descrizione']
    list_filter = ['nome', 'id', 'descrizione']


@admin.register(Ufficio)
class UfficioModelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id', 'descrizione']
    search_fields = ['nome', 'id', 'descrizione']
    list_filter = ['nome', 'id', 'descrizione']


@admin.register(QualificaUfficio)
class QualificaUfficioModelAdmin(admin.ModelAdmin):
    list_display = ['ufficio', 'qualifica']
    search_fields = ['ufficio', 'qualifica']
    list_filter = ['ufficio', 'qualifica']


@admin.register(Assegnatario)
class AssegnatarioUfficioModelAdmin(admin.ModelAdmin):
    list_display = ['utente', 'qualifica_ufficio']
    search_fields = ['utente', 'qualifica_ufficio']
    list_filter = ['utente', 'qualifica_ufficio']



# @admin.register(OrganizationType)
# class OrganizationTypeModelAdmin(admin.ModelAdmin):
#     list_display = ['name', 'code', 'description']
#     search_fields = ['name', 'code', 'description']
#     list_filter = ['name', 'code', 'description']


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return("%s (%s)" % (obj.name, obj.organization_type))


class UserMembershipModelAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserMembershipModelAdminForm, self).__init__(*args, **kwargs)
        self.fields['type'] = MyModelChoiceField(queryset=self.fields['type'].queryset)


# @admin.register(Ruolo)
# class RuoloModelAdmin(admin.ModelAdmin):
#     form = UserMembershipModelAdminForm
#     list_display = ['utente', 'qualifica', 'ente', 'profilo']
#     search_fields = ['utente', 'ente__nome', 'utente__fiscal_code', 'utente__first_name', 'utente__last_name', 'qualifica__name']
#     list_filter = ['utente', 'qualifica', 'ente', 'profilo']


# @admin.register(Qualifica)
# class QualificaModelAdmin(admin.ModelAdmin):
#     list_display = ['nome', 'id', 'descrizione']
#     search_fields = ['nome', 'id', 'descrizione']
#     list_filter = ['nome', 'id', 'descrizione']


@admin.register(Utente)
class UtenteAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('fiscal_code', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('fiscal_code', 'password1', 'password2'),
        }),
    )
    list_display = ('fiscal_code', 'email', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_active', 'groups')
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('fiscal_code', 'first_name', 'last_name', 'email')
    ordering = ('fiscal_code',)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'view_user', 'expires')
    search_fields = ('key', 'user', 'expires')
    # list_filter = ('key', 'user', 'expires')

    def view_user(self, obj):
        return obj.user
    view_user.empty_value_display = '== Non assegnato =='

