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


class OrganizationType(models.Model):
    """
    Organizations Type
    """

    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = _('Tipo di ente')
        verbose_name_plural = _('Tipi di ente')


class Organization(models.Model):
    """
    Organizations (also called 'Ente') wich can deal with Statuto Del Territorio
    """

    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    type = models.OneToOneField(OrganizationType, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Ente')
        verbose_name_plural = _('Enti')


class AppUser(AbstractUser):
    """
    Statuto del Territorio Base User.
    Fiscal code is a required/unique extra field.
    Organization is an optional field.
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

    # TODO: organization manytomany, proceedings manytomany

    REQUIRED_FIELDS = ['fiscal_code', 'email']

    class Meta:
        ordering = [
            "date_joined",
        ]
        verbose_name = _('Utente')
        verbose_name_plural = _('Utenti')



class State(object):
    """
    Abstract State Class.
    """

    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    max_duration = models.IntegerField(null=True, blank=True)


class ProceedingsMicroState(State, models.Model):
    """
    Proceedings Micro State.
    A State is defined 'Micro' when a 'micro' proceedings (internal proceedings of a Macro proceedings) is accomplished.
    A Macro proceedings could has more than one active 'micro' proceedings so more than one active Micro state.

    """

    class Meta:
        verbose_name = _('Micro stato')
        verbose_name_plural = _('Micro stati')


class ProceedingsMacroState(State, models.Model):
    """
    Proceedings Macro State.
    A State is defined 'Macro' when a 'macro' proceedings has been accomplished

    """

    micro_state = models.ForeignKey(ProceedingsMicroState, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Macro stato')
        verbose_name_plural = _('Macro stati')


class ProceedingsType(models.Model):
    """
    Proceedings Type
    """

    code = models.CharField(max_length=50,  primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = _('Tipo di procedimento')
        verbose_name_plural = _('Tipi di procedimento')


class ProceedingsRegistry(models.Model):
    """
    Proceedings Registry (also called 'Anagrafica')
    """

    id = models.CharField(max_length=50,  primary_key=True)
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    type = models.OneToOneField(ProceedingsType, on_delete=models.SET_NULL, null=True)
    RUP = models.OneToOneField(AppUser, on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    created_by = models.OneToOneField(AppUser, on_delete=models.SET_NULL, null=True)
    creation_date = models.DateTimeField(null=False, blank=False)
    accomplishment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Anagrafica del piano')
        verbose_name_plural = _('Anagrafiche dei piani')


class Proceedings(models.Model):
    """
    Statuto del Territorio Proceedings.
    """

    macro_state = models.OneToOneField(ProceedingsMacroState, on_delete=models.SET_NULL, null=True)
    owner = models.OneToOneField(AppUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Procedimento')
        verbose_name_plural = _('Procedimenti')



