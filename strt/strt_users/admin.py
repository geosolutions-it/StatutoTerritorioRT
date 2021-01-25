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

import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .enums import Profilo, Qualifica
from .models import (Utente, Ente, Ufficio, QualificaUfficio, Assegnatario, Token, ProfiloUtente)
from django.utils.translation import gettext_lazy as _

from django.db.models.fields import Field

from django.core import exceptions

logger = logging.getLogger(__name__)


def field_validate_monkey_patch(self, value, model_instance):
    """
    Validate value and raise ValidationError if necessary. Subclasses
    should override this to provide validation logic.
    """
    if not self.editable:
        # Skip validation for non-editable fields.
        return

    text_value = str(value)
    if self.choices and value not in self.empty_values:
        for option_key, option_value in self.choices:
            if isinstance(option_value, (list, tuple)):
                # This is an optgroup, so look inside the group for
                # options.
                for optgroup_key, optgroup_value in option_value:
                    if value == optgroup_key:
                        return
            elif value == option_key or text_value == str(option_key):
                return
        raise exceptions.ValidationError(
            self.error_messages['invalid_choice'],
            code='invalid_choice',
            params={'value': value},
        )

    if value is None and not self.null:
        raise exceptions.ValidationError(self.error_messages['null'], code='null')

    if not self.blank and value in self.empty_values:
        raise exceptions.ValidationError(self.error_messages['blank'], code='blank')


logger.warning('*** MONKEY PATCHING django.db.models.fields.Field.validate')
Field.validate = field_validate_monkey_patch

admin.site.empty_value_display = "(Vuoto)"


@admin.register(Ente)
class EnteModelAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'nome', 'ipa', 'descrizione']
    search_fields = ['nome', 'ipa', 'descrizione']
    list_filter = ['tipo']

    list_display_links = ['nome', 'ipa']
    ordering = ['nome']

@admin.register(Ufficio)
class UfficioModelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'ente', 'descrizione']
    search_fields = ['nome', 'id', 'descrizione']
    list_filter = ['ente']


# class QualificaFilter(admin.SimpleListFilter):
#     title = _('Qualifica')
#     parameter_name = 'qualifica'
#
#     def lookups(self, request, model_admin):
#         return Qualifica.create_dropdown()
#
#     def queryset(self, request, queryset):
#         return queryset.filter(qualifica=Qualifica.fix_enum(self.value())) if self.value() else queryset


@admin.register(QualificaUfficio)
class QualificaUfficioModelAdmin(admin.ModelAdmin):
    list_display = ['ufficio', 'qualifica', 'is_soggetto_default']
    search_fields = ['ufficio']
    list_filter = ['qualifica', "ufficio__ente", 'is_soggetto_default']

    def get_list_display(self, request):
        return self.list_display

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Questo metodo serve perchè su DB le choice hanno forma "ENUMNAME.name",
        mentre la form default la gestirebbe come lista di "name"
        """
        if db_field.name == "qualifica":
            kwargs['choices'] = Qualifica.create_choices()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        qualifica non deve essere modificabile, altrimenti si rischia di modificare la funzione degli assegnatari
        senza che ne abbiano le competenze
        """
        if obj:
            # return ['ufficio', ]
            return ['ufficio', 'qualifica',]
        else:
            return []


@admin.register(Assegnatario)
class AssegnatarioModelAdmin(admin.ModelAdmin):
    list_display = ['_utente', 'qualifica', 'ufficio', 'ente']
    search_fields = ['utente', 'qualifica_ufficio_ufficio']
    list_filter = ['qualifica_ufficio__qualifica', 'qualifica_ufficio__ufficio__ente']

    ordering = ['utente__last_name', 'utente__first_name']

    def _utente(self, obj):
        return "{} {}".format(obj.utente.last_name or "--", obj.utente.first_name or "--")

    _utente.admin_order_field = 'utente__last_name'

    def qualifica(self, obj):
        return obj.qualifica_ufficio.qualifica.value

    qualifica.admin_order_field = 'qualifica_ufficio__qualifica'

    def ufficio(self, obj):
        return obj.qualifica_ufficio.ufficio.nome

    ufficio.admin_order_field = 'qualifica_ufficio__ufficio__nome'

    def ente(self, obj):
        return obj.qualifica_ufficio.ufficio.ente.nome

    ente.admin_order_field = 'qualifica_ufficio__ufficio__ente__nome'


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
    list_display = ('fiscal_code', 'last_name', 'first_name', 'email')
    list_filter = ('is_superuser', 'is_active', 'groups')
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('fiscal_code', 'first_name', 'last_name', 'email')
    ordering = ('fiscal_code',)


@admin.register(ProfiloUtente)
class ProfiloUtenteAdmin(admin.ModelAdmin):
    list_display = ['_utente', '_cf', 'ente', 'profilo']
    search_fields = ['utente', 'ente', 'profilo']
    list_filter = ['ente', 'profilo']

    def _utente(self, obj):
        return "{} {}".format(obj.utente.last_name or "--", obj.utente.first_name or "--")

    _utente.admin_order_field = 'utente__last_name'

    def _cf(self, obj):
        return obj.utente.fiscal_code

    _cf.short_description = "Codice fiscale"


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'view_user', 'expires')
    search_fields = ('key', 'user', 'expires')

    def view_user(self, obj):
        return obj.user

    view_user.empty_value_display = '== Non assegnato =='
