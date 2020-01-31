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

import os
import logging
import binascii
import traceback

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_currentuser.db.models import CurrentUserField

from .enums import (
    Qualifica,
    Profilo,
    TipoEnte,
)
from .managers import AppUserManager


logger = logging.getLogger(__name__)


# class AppPriv(models.Model):
#     """
#     A single privilege in the SERAPIDE application: e.g.: admin_user, create_plan, manage_plan
#     """
#     name = models.CharField(max_length=20, primary_key=True)
#     description = models.CharField(max_length=250)
#     created = models.DateTimeField(auto_now_add=True)
#
#     def __unicode__(self):
#         return self.name

# class Profilo(models.Model):
#     """
#     A set of privileges: e.g.: ISIDE(admin_user), RUP(admin_user, create_plan, manage_plan), ...
#     """
#     id = models.AutoField(
#         auto_created=True, primary_key=True, serialize=False, verbose_name=_('id')
#     )
#     nome = models.CharField(
#         max_length=255, null=False, blank=False, verbose_name=_('nome')
#     )
#     descrizione = models.TextField(
#         max_length=500, null=True, blank=True, verbose_name=_('descrizione')
#     )
#
#     def __unicode__(self):
#         return self.name
#
#
# class Grant(models.Model):
#     """
#     A single privilege in the SERAPIDE application: e.g.: admin_user, create_plan, manage_plan
#     """
#     priv = models.CharField(choices=PRIVILEGIO, max_length=20)
#     profilo = models.ForeignKey(Profilo, on_delete=models.CASCADE)
#
#     def __unicode__(self):
#         return self.priv

class Utente(AbstractBaseUser, PermissionsMixin):
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
        verbose_name=_('nome'), max_length=255, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name=_('cognome'), max_length=255, blank=True, null=True
    )
    email = models.EmailField(
        verbose_name=_('indirizzo email'), blank=True, null=True
    )
    # is_staff = models.BooleanField(
    #     _('staff status'),
    #     default=False,
    #     help_text=_('Designates whether the user can log into this admin site.'),
    # )
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
        if self.first_name or self.last_name:
            first_name = self.first_name if self.first_name else ''
            last_name = self.last_name if self.last_name else ''
            return "{} {}".format(first_name, last_name)
        else:
            return self.fiscal_code.upper()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return "{} {}".format(self.last_name.title(), self.first_name.title())
        else:
            return self.fiscal_code.upper()

    def get_short_name(self):
        if self.first_name and self.last_name:
            return self.first_name.title()
        else:
            return self.fiscal_code.upper()

    # def get_ruoli(self):
    #     """
    #     User membership type for each organization
    #     :return: UserMembership queryset
    #     """
    #     return Ruolo._default_manager.filter(utente=self)

    class Meta:
        ordering = [
            'date_joined',
        ]
        verbose_name = _('utente')
        verbose_name_plural = _('utenti')


class Ente(models.Model):
    """
    Organizations (also called 'Ente') wich can deal with Statuto Del Territorio
    """

    id = models.CharField(
        max_length=50, primary_key=True, verbose_name=_('id')
    )
    ipa = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('codice ipa')
    )
    nome = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    descrizione = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )

    tipo = models.CharField(choices=TipoEnte.create_choices(), max_length=8, null=False)

    class Meta:
        verbose_name = _('ente')
        verbose_name_plural = _('enti')

    def __str__(self):
        return self.nome

    def is_comune(self):
        return self.tipo == TipoEnte.COMUNE


class UserType(models.Model):

    utente = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE, null=False)
    profilo = models.CharField(choices=Profilo.create_choices(), max_length=16, null=False)
    ente = models.ForeignKey(Ente, related_name="+", on_delete=models.CASCADE)

    def __str__(self):
        return "{profilo}:{utente}@{ente}".format(
            profilo=self.profilo.name,
            utente=self.utente.fiscal_code,
            ente=self.ente)


class Ufficio(models.Model):
    """

    """

    id = models.CharField(
        max_length=50, primary_key=True, verbose_name=_('id')
    )
    nome = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    descrizione = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )
    ente = models.ForeignKey(Ente, related_name="+", on_delete=models.CASCADE)

    email = models.EmailField(
        verbose_name=_('indirizzo email'), blank=True, null=True
    )

    # qualifica = models.ForeignKey(Qualifica, related_name="qualifica", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class QualificaUfficio(models.Model):
    """

    """

    id = models.CharField(
        max_length=50, primary_key=True, verbose_name=_('id')
    )

    ufficio = models.ForeignKey(Ufficio, related_name="+", on_delete=models.CASCADE)
    qualifica = models.CharField(choices=Qualifica.create_choices(), max_length=8, null=False)

    def __str__(self):
        return self.qualifica + '::' + self.ufficio.name


class Assegnatario(models.Model):
    """

    """

    qualifica_ufficio = models.ForeignKey(QualificaUfficio, related_name="+", on_delete=models.CASCADE)

    utente = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE)

    def __str__(self):
        return self.qualifica + '::' + self.utente + " @" + self.ufficio.name





#
# class Ruolo(models.Model):
#     """
#
#     """
#     id = models.AutoField(
#         auto_created=True, primary_key=True, serialize=False, verbose_name=_('id')
#     )
#
#     ente = models.ForeignKey(Ente, related_name="ente+", on_delete=models.CASCADE, null=False)
#     profilo = models.ForeignKey(Profilo, related_name="profilo+", on_delete=models.CASCADE, null=False)
#     qualifica = models.ForeignKey(Qualifica, related_name="qualifica+", on_delete=models.CASCADE, null=True)
#     utente = models.ForeignKey(Utente, related_name="utente+", on_delete=models.CASCADE, null=False)
#
#     def __unicode__(self):
#         return "U:{utente} E:{ente} P:{profilo} Q:{qualifica}".format(
#             utente=self.utente,
#             profilo=self.profilo,
#             ente=self.ente,
#             qualifica=self.qualifica if self.qualifica else "-",
#         )
#

# class AppUser(AbstractBaseUser, PermissionsMixin):
#     """
#     Statuto del Territorio Base User.
#     Fiscal code is a required/unique extra field.
#     """
#
#     fiscal_code = models.CharField(
#         verbose_name=_('codice fiscale'), max_length=16,
#         help_text=_('inserire un codice fiscale valido'),
#         validators=[
#             RegexValidator(
#                 regex='^(?i)(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|'
#                       '[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\dLMNP-V]{2}(?:[A-EHLMPR-T]'
#                       '(?:[04LQ][1-9MNP-V]|[1256LMRS][\dLMNP-V])|[DHPS][37PT][0L]|'
#                       '[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L]'
#                       '(?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$',
#                 message=_('Codice fiscale errato.'),
#             ),
#         ],
#         unique=True, db_index=True, blank=False, null=False,
#     )
#     first_name = models.CharField(
#         verbose_name=_('nome'), max_length=255, blank=True, null=True
#     )
#     last_name = models.CharField(
#         verbose_name=_('cognome'), max_length=255, blank=True, null=True
#     )
#     email = models.EmailField(
#         verbose_name=_('indirizzo email'), blank=True, null=True
#     )
#     is_staff = models.BooleanField(
#         _('staff status'),
#         default=False,
#         help_text=_('Designates whether the user can log into this admin site.'),
#     )
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#         help_text=_(
#             'Designates whether this user should be treated as active. '
#             'Unselect this instead of deleting accounts.'
#         ),
#     )
#     date_joined = models.DateTimeField(
#         verbose_name=_('data creazione'), auto_now_add=True
#     )
#     date_updated = models.DateTimeField(
#         verbose_name=_('data ultima modifica'), auto_now=True
#     )
#     created_by = CurrentUserField(
#         verbose_name=_('creato da'), editable=False,
#         related_name='%(class)s_created'
#     )
#     updated_by = CurrentUserField(
#         verbose_name=_('modificato da'), editable=False,
#         related_name='%(class)s_updated'
#     )
#
#     EMAIL_FIELD = 'email'
#     USERNAME_FIELD = 'fiscal_code'
#
#     objects = AppUserManager()
#
#     def __str__(self):
#         if self.first_name or self.last_name:
#             first_name = self.first_name if self.first_name else ''
#             last_name = self.last_name if self.last_name else ''
#             return "{} {}".format(first_name, last_name)
#         else:
#             return self.fiscal_code.upper()
#
#     def get_full_name(self):
#         if self.first_name and self.last_name:
#             return "{} {}".format(self.last_name.title(), self.first_name.title())
#         else:
#             return self.fiscal_code.upper()
#
#     def get_short_name(self):
#         if self.first_name and self.last_name:
#             return self.first_name.title()
#         else:
#             return self.fiscal_code.upper()
#
#     @property
#     def memberships(self):
#         """
#         User membership type for each organization
#         :return: UserMembership queryset
#         """
#         return UserMembership._default_manager.filter(member=self)
#
#     class Meta:
#         ordering = [
#             'date_joined',
#         ]
#         verbose_name = _('utente')
#         verbose_name_plural = _('utenti')

class Delega(models.Model):
    """
    An access token that is associated with a user.
    This is essentially the same as the token model from Django REST Framework
    """
    key = models.CharField(max_length=40, primary_key=True)
#    user = models.ForeignKey(AppUser, related_name="user", on_delete=models.CASCADE)
#    membership = models.ForeignKey('UserMembership', related_name="role", on_delete=models.CASCADE)
    user = models.ForeignKey(Utente, related_name="user", on_delete=models.CASCADE)
#    qualifica = models.ForeignKey(Qualifica, related_name="qualifica", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Delega, self).save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires

    def __unicode__(self):
        return self.key



# class Token(models.Model):
#     """
#     An access token that is associated with a user.
#     This is essentially the same as the token model from Django REST Framework
#     """
#     key = models.CharField(max_length=40, primary_key=True)
#     user = models.ForeignKey(AppUser, related_name="user", on_delete=models.CASCADE)
#     membership = models.ForeignKey('UserMembership', related_name="role", on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True)
#     expires = models.DateTimeField()
#
#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super(Token, self).save(*args, **kwargs)
#
#     @classmethod
#     def generate_key(cls):
#         return binascii.hexlify(os.urandom(20)).decode()
#
#     def is_expired(self):
#         """
#         Check token expiration with timezone awareness
#         """
#         if not self.expires:
#             return True
#
#         return timezone.now() >= self.expires
#
#     def __unicode__(self):
#         return self.key


# class OrganizationType(models.Model):
#     """
#     Organizations Type
#     """
#
#     code = models.CharField(
#         max_length=50, primary_key=True, verbose_name=_('codice')
#     )
#     name = models.CharField(
#         max_length=255, null=False, blank=False, verbose_name=_('nome')
#     )
#     description = models.TextField(
#         max_length=500, null=True, blank=True, verbose_name=_('descrizione')
#     )
#
#     class Meta:
#         verbose_name = _('tipo di ente')
#         verbose_name_plural = _('tipi di ente')
#
#     def __str__(self):
#         return self.name


# class Organization(models.Model):
#     """
#     Organizations (also called 'Ente') wich can deal with Statuto Del Territorio
#     """
#
#     code = models.CharField(
#         max_length=50, primary_key=True, verbose_name=_('codice')
#     )
#     name = models.CharField(
#         max_length=255, null=False, blank=False, verbose_name=_('nome')
#     )
#     description = models.TextField(
#         max_length=500, null=True, blank=True, verbose_name=_('descrizione')
#     )
#     type = models.ForeignKey(
#         to='OrganizationType', on_delete=models.CASCADE, verbose_name=_('tipo'),
#         default=None, blank=True, null=True
#     )
#
#     class Meta:
#         verbose_name = _('ente')
#         verbose_name_plural = _('enti')
#
#     def __str__(self):
#         return self.name
#
#
# class MembershipType(models.Model):
#     """
#     Role types
#     """
#
#     code = models.CharField(
#         max_length=50, null=False, blank=False, verbose_name=_('codice')
#     )
#     name = models.CharField(
#         max_length=255, null=False, blank=False, verbose_name=_('nome')
#     )
#     description = models.TextField(
#         max_length=500, null=True, blank=True, verbose_name=_('descrizione')
#     )
#     organization_type = models.ForeignKey(
#         to='OrganizationType', on_delete=models.CASCADE, verbose_name=_('tipo di ente'),
#         default=None, blank=True, null=True
#     )
#
#     class Meta:
#         unique_together = ('code', 'name', 'organization_type')
#         verbose_name = _('tipo di ruolo')
#         verbose_name_plural = _('tipi di ruolo')
#
#     def __str__(self):
#         return '{}'.format(self.name)
#
#
# class UserMembership(models.Model):
#     """
#     Roles
#     """
#
#     code = models.AutoField(
#         auto_created=True, primary_key=True, serialize=False, verbose_name=_('codice')
#     )
#     name = models.CharField(
#         max_length=255, null=False, blank=False, verbose_name=_('nome')
#     )
#     description = models.TextField(
#         max_length=500, null=True, blank=True, verbose_name=_('descrizione')
#     )
#     member = models.ForeignKey(
#         to='AppUser', on_delete=models.CASCADE, verbose_name=_('utente'),
#         default=None, blank=True, null=True
#     )
#     organization = models.ForeignKey(
#         to='Organization', on_delete=models.CASCADE, verbose_name=_('ente'),
#         default=None, blank=True, null=True
#     )
#     type = models.ForeignKey(
#         to='MembershipType', on_delete=models.CASCADE, verbose_name=_('tipo'),
#         default=None, blank=True, null=True
#     )
#     date_joined = models.DateTimeField(
#         verbose_name=_('data creazione'), auto_now_add=True
#     )
#     date_updated = models.DateTimeField(
#         verbose_name=_('data ultima modifica'), auto_now=True
#     )
#     created_by = CurrentUserField(
#         verbose_name=_('creato da'), editable=False,
#         related_name='%(class)s_created'
#     )
#     updated_by = CurrentUserField(
#         verbose_name=_('modificato da'), editable=False,
#         related_name='%(class)s_updated'
#     )
#     attore = models.CharField(
#         choices=TIPOLOGIA_ATTORE,
#         default=TIPOLOGIA_ATTORE.unknown,
#         max_length=80
#     )
#
#     class Meta:
#         unique_together = ('code', 'member', 'organization', 'type')
#         verbose_name = _('ruolo')
#         verbose_name_plural = _('ruoli')
#
#     def __str__(self):
#         return self.name


# ############################################################################ #
# Model Signals
# ############################################################################ #
def do_login(sender, user, request, **kwargs):
    if user and user.is_authenticated:
        token = None
        try:
            token = request.GET.get('token', None)

            if token is None:
                auth_header = request.META.get('HTTP_AUTHORIZATION', b'').split()
                if auth_header and auth_header[0].lower() == b'token':
                    if len(auth_header) == 2:
                        token = auth_header[1]
        except BaseException:
            tb = traceback.format_exc()
            logger.debug(tb)

        if token:
            request.session['token'] = token


def do_logout(sender, user, request, **kwargs):
    if 'organization' in request.session:
        del request.session['organization']

    if 'token' in request.session:
        del request.session['token']

    request.session.modified = True


user_logged_in.connect(do_login)
user_logged_out.connect(do_logout)
