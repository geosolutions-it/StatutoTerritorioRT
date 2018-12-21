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

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, AbstractUser
)
from django.utils.translation import ugettext_lazy as _
from .managers import AppUserManager
from django_currentuser.db.models import CurrentUserField


class AppUser(AbstractBaseUser, PermissionsMixin):
    """
    Statuto del Territorio Base User.
    Fiscal code is a required/unique extra field.
    """

    fiscal_code = models.CharField(
        verbose_name=_('codice fiscale'), max_length=16,
        help_text=_('inserire un codice fiscale valido'),
        validators=[
            RegexValidator(
                regex='^(?i)(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|'
                      '[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\dLMNP-V]{2}(?:[A-EHLMPR-T]'
                      '(?:[04LQ][1-9MNP-V]|[1256LMRS][\dLMNP-V])|[DHPS][37PT][0L]|'
                      '[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L]'
                      '(?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$',
                message=_('Codice fiscale errato.'),
            ),
        ],
        unique=True, db_index=True, blank=False, null=False,
    )
    first_name = models.CharField(
        verbose_name=_('nome'), max_length=30, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name=_('cognome'), max_length=150, blank=True, null=True
    )
    email = models.EmailField(
        verbose_name=_('indirizzo email'), blank=True, null=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        verbose_name=_('data creazione'), auto_now_add=True
    )
    date_updated = models.DateTimeField(
        verbose_name=_('data ultima modifica'), auto_now=True
    )
    created_by = CurrentUserField(
        verbose_name=_('creato da'), editable=False,
        related_name='%(class)s_created'
    )
    updated_by = CurrentUserField(
        verbose_name=_('modificato da'), editable=False,
        related_name='%(class)s_updated'
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'fiscal_code'

    objects = AppUserManager()

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.last_name.title()} {self.first_name.title()}'
        else:
            return self.fiscal_code.upper()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.last_name.title()} {self.first_name.title()}'
        else:
            return self.fiscal_code.upper()

    def get_short_name(self):
        if self.first_name and self.last_name:
            return self.first_name.title()
        else:
            return self.fiscal_code.upper()

    @property
    def memberships(self):
        """
        User membership type for each organization
        :return: UserMembership queryset
        """
        return UserMembership._default_manager.filter(member=self)

    class Meta:
        ordering = [
            'date_joined',
        ]
        verbose_name = _('utente')
        verbose_name_plural = _('utenti')


class OrganizationType(models.Model):
    """
    Organizations Type
    """

    code = models.CharField(
        max_length=50, primary_key=True, verbose_name=_('codice')
    )
    name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    description = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )

    class Meta:
        verbose_name = _('tipo di ente')
        verbose_name_plural = _('tipi di ente')

    def __str__(self):
        return self.name


class Organization(models.Model):
    """
    Organizations (also called 'Ente') wich can deal with Statuto Del Territorio
    """

    code = models.CharField(
        max_length=50, primary_key=True, verbose_name=_('codice')
    )
    name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    description = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )
    type = models.ForeignKey(
        to='OrganizationType', on_delete=models.CASCADE, verbose_name=_('tipo'),
        default=None, blank=True, null=True
    )

    class Meta:
        verbose_name = _('ente')
        verbose_name_plural = _('enti')

    def __str__(self):
        return self.name


class MembershipType(models.Model):
    """
    Role types
    """

    code = models.CharField(
        max_length=50, null=False, blank=False, verbose_name=_('codice')
    )
    name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    description = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )
    organization_type = models.ForeignKey(
        to='OrganizationType', on_delete=models.CASCADE, verbose_name=_('tipo di ente'),
        default=None, blank=True, null=True
    )

    class Meta:
        unique_together = ('code', 'organization_type')
        verbose_name = _('tipo di ruolo')
        verbose_name_plural = _('tipi di ruolo')

    def __str__(self):
        return self.name


class UserMembership(models.Model):
    """
    Roles
    """

    code = models.AutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name=_('codice')
    )
    name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    description = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )
    member = models.ForeignKey(
        to='AppUser', on_delete=models.CASCADE, verbose_name=_('utente'),
        default=None, blank=True, null=True
    )
    organization = models.ForeignKey(
        to='Organization', on_delete=models.CASCADE, verbose_name=_('ente'),
        default=None, blank=True, null=True
    )
    type = models.ForeignKey(
        to='MembershipType', on_delete=models.CASCADE, verbose_name=_('tipo'),
        default=None, blank=True, null=True
    )
    date_joined = models.DateTimeField(
        verbose_name=_('data creazione'), auto_now_add=True
    )
    date_updated = models.DateTimeField(
        verbose_name=_('data ultima modifica'), auto_now=True
    )
    created_by = CurrentUserField(
        verbose_name=_('creato da'), editable=False,
        related_name='%(class)s_created'
    )
    updated_by = CurrentUserField(
        verbose_name=_('modificato da'), editable=False,
        related_name='%(class)s_updated'
    )

    class Meta:
        unique_together = ('member', 'organization', 'type')
        verbose_name = _('ruolo')
        verbose_name_plural = _('ruoli')

    def __str__(self):
        return self.name
