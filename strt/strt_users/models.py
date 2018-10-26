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
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import ugettext_lazy as _


class AppUser(AbstractUser):
    """
    Statuto del Territorio Base User.
    Fiscal code is a required/unique extra field.
    """

    fiscal_code = models.CharField(
        verbose_name=_('codice fiscale'),
        max_length=16,
        validators=[
            RegexValidator(
                regex='^(?i)(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\dLMNP-V]{2}(?:[A-EHLMPR-T](?:[04LQ][1-9MNP-V]|[1256LMRS][\dLMNP-V])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L](?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$',
                message=_('Codice fiscale errato.'),
            ),
        ],
        unique=True,
    )

    REQUIRED_FIELDS = ['fiscal_code', 'email']

    class Meta:
        ordering = [
            "date_joined",
        ]
        verbose_name = _('Utente')
        verbose_name_plural = _('Utenti')


class OrganizationType(models.Model):
    """
    Organizations Type
    """

    code = models.CharField(verbose_name=_('codice'), max_length=50, primary_key=True)
    name = models.CharField(verbose_name=_('nome'), max_length=255, null=False, blank=False)
    description = models.TextField(verbose_name=_('descrizione'), max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = _('Tipo di ente')
        verbose_name_plural = _('Tipi di ente')

    def __str__(self):
        return '{} -  {}'.format(self.code, self.name)


class Organization(models.Model):
    """
    Organizations (also called 'Ente') wich can deal with Statuto Del Territorio
    """

    code = models.CharField(verbose_name=_('codice'), max_length=50, primary_key=True)
    name = models.CharField(verbose_name=_('nome'), max_length=255, null=False, blank=False)
    description = models.TextField(verbose_name=_('descrizione'), max_length=500, null=True, blank=True)
    type = models.ForeignKey('OrganizationType', on_delete=models.SET_NULL, null=True)
    users = models.ManyToManyField('AppUser', through='UserMembership')

    class Meta:
        verbose_name = _('Ente')
        verbose_name_plural = _('Enti')

    def __str__(self):
        return '{} -  {}'.format(self.code, self.name)


class MembershipType(models.Model):
    """
    Role types
    """

    code = models.CharField(verbose_name=_('codice'), max_length=50, primary_key=True)
    name = models.CharField(verbose_name=_('nome'), max_length=255, null=False, blank=False)
    description = models.TextField(verbose_name=_('descrizione'), max_length=500, null=True, blank=True)
    organization = models.ManyToManyField('Organization', through='UserMembership', verbose_name=_('Ente'))
    organization_type = models.ForeignKey('OrganizationType', on_delete=models.SET_NULL, null=True, verbose_name=_('Tipo di ente'))

    class Meta:
        verbose_name = _('Tipo di ruolo')
        verbose_name_plural = _('Tipi di ruolo')

    def __str__(self):
        return '{} -  {}'.format(self.code, self.name)


class UserMembership(Group):
    """
    Roles
    """

    code = models.CharField(verbose_name=_('codice'), max_length=50, primary_key=True)
    description = models.TextField(verbose_name=_('descrizione'), max_length=500, null=True, blank=True)
    member = models.ForeignKey('AppUser', on_delete=models.SET_NULL, null=True, verbose_name=_('Utente'))
    membership_type = models.ForeignKey('MembershipType', on_delete=models.SET_NULL, null=True, verbose_name=_('Tipo di ruolo'))
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, verbose_name=_('Ente'))

    class Meta:
        verbose_name = _('Ruolo')
        verbose_name_plural = _('Ruoli')

    def __str__(self):
        return '{} -  {}'.format(self.code, self.name)