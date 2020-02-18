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
import os
import traceback
import binascii
import uuid

from django.dispatch import receiver
from django.db.models.signals import post_init

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
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
from .managers import IsideUserManager

logger = logging.getLogger(__name__)


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
        unique=True, db_index=True, blank=False, null=False, primary_key=True
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

    objects = IsideUserManager()

    def __str__(self):
        if self.first_name or self.last_name:
            first_name = self.first_name if self.first_name else ''
            last_name = self.last_name if self.last_name else ''
            return "Utente[{} - {} {}]".format(self.fiscal_code.upper(), first_name, last_name)
        else:
            return "Utente[{}]".format(self.fiscal_code.upper())

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

    # id = models.CharField(
    #     max_length=50, primary_key=True, verbose_name=_('id')
    # )
    ipa = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('codice ipa')
    )
    nome = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_('nome')
    )
    descrizione = models.TextField(
        max_length=500, null=True, blank=True, verbose_name=_('descrizione')
    )

    tipo = models.CharField(choices=TipoEnte.create_choices(), max_length=24, null=False)

    class Meta:
        verbose_name = _('ente')
        verbose_name_plural = _('enti')

    def __str__(self):
        return "{nome} ({ipa})".format(nome=self.nome, ipa=self.ipa)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Ente, cls).from_db(db, field_names, values)
        instance.tipo = TipoEnte.fix_enum(instance.tipo)
        return instance

    def is_comune(self):
        return self.tipo == TipoEnte.COMUNE


class ProfiloUtente(models.Model):

    utente = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE, null=False)
    profilo = models.CharField(choices=Profilo.create_choices(), max_length=32, null=False)
    ente = models.ForeignKey(Ente, related_name="+", on_delete=models.CASCADE, null=True)

    def __str__(self):
        p = self.profilo.name if isinstance(self.profilo, Profilo) else "!!!{}".format(self.profilo)

        return "{profilo}:{utente}@{ente}".format(
            profilo=p,
            utente=self.utente.fiscal_code,
            ente=self.ente)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(ProfiloUtente, cls).from_db(db, field_names, values)
        instance.profilo = Profilo.fix_enum(instance.profilo)
        return instance

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='No ENTE for global admins',
                check= ~Q(profilo = Profilo.ADMIN_PORTALE) |
                       ( Q(profilo = Profilo.ADMIN_PORTALE) & Q(ente__isnull = True))),
            models.CheckConstraint(
                name='ENTE required for non-admins',
                check= Q(profilo = Profilo.ADMIN_PORTALE) |
                       ( ~Q(profilo = Profilo.ADMIN_PORTALE) & Q(ente__isnull = False))),
        ]

# @receiver(post_init, sender=ProfiloUtente)
# def fix_profilo_enum(sender, instance, **kwargs):
#     instance.profilo = Profilo.fix_enum(instance.profilo)


class Ufficio(models.Model):
    """

    """

    # id = models.CharField(
    #     max_length=50, primary_key=True, verbose_name=_('id')
    # )
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False,
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
        return self.nome


# ALLOWED_ENTE = {
#     Qualifica.RESP: [TipoEnte.COMUNE],
#     Qualifica.AC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
#     Qualifica.SCA: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
#     Qualifica.GC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
#     Qualifica.PIAN: [TipoEnte.REGIONE],
#     Qualifica.URB: [TipoEnte.REGIONE],
#     Qualifica.READONLY: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
# }
#
# def _create_qualificaufficio_constraint():
#     constraint = None
#     for qualifica, tipi in ALLOWED_ENTE.items():
#         q = Q(qualifica = qualifica) & Q(ufficio__ente__tipo__in = tipi)
#         constraint = q | constraint if constraint else q
#     return constraint

class QualificaUfficio(models.Model):
    """

    """
    ufficio = models.ForeignKey(Ufficio, related_name="+", on_delete=models.CASCADE)
    qualifica = models.CharField(choices=Qualifica.create_choices(), max_length=32, null=False)

    def __str__(self):
        q = self.qualifica.name if isinstance(self.qualifica, Qualifica) else "!!!{}".format(self.qualifica)

        return '{qualifica}::{nome}'.format(
            qualifica= q,
            # qualifica=Qualifica[self.qualifica],
            nome=self.ufficio.nome)

    class Meta:
        pass
        # constraints = [
        #     # Next constr would generate a "django.core.exceptions.FieldError: Joined field references are not permitted in this query"
        #     models.CheckConstraint(
        #         name='Qualifica ristretta per ente',
        #         # check= Q(ufficio__ente__tipo__in =  Qualifica._ALLOWED_ENTE[qualifica]))
        #         check = _create_qualificaufficio_constraint())
        # ]

    def _check_allowed_qualifica(self):
        if not self.qualifica.is_allowed(self.ufficio.ente.tipo):
            raise ValidationError('Qualifica "{qualifica}" non permessa per ufficio [{ufficio}] per ente [{ente}] {tipo}'.format(
                qualifica=self.qualifica,
                ufficio=self.ufficio,
                ente=self.ufficio.ente,
                tipo=self.ufficio.ente.tipo
            ))

    # OVERRIDE
    def save(self, *args, **kwargs):
        self._check_allowed_qualifica()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(QualificaUfficio, cls).from_db(db, field_names, values)
        instance.qualifica = Qualifica.fix_enum(instance.qualifica)
        return instance


# @receiver(post_init, sender=QualificaUfficio)
# def fix_qualifica_enum(sender, instance, **kwargs):
#     instance.qualifica = Qualifica.fix_enum(instance.qualifica)


class Assegnatario(models.Model):
    """
        Qualifiche fisse assegnate ad un utente da parte di un ufficio
    """
    qualifica_ufficio = models.ForeignKey(QualificaUfficio, related_name="+", on_delete=models.CASCADE)
    utente = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE)

    def __str__(self):
        return '{qu}::{utente} @{ufficio}'.format(
            qu=self.qualifica_ufficio,
            utente=self.utente,
            ufficio=self.qualifica_ufficio.ufficio.nome)

    def _check_user_is_op(self):
        if not ProfiloUtente.objects\
                .filter(utente=self.utente) \
                .filter(ente=self.qualifica_ufficio.ufficio.ente) \
                .filter(profilo=Profilo.OPERATORE)\
                .exists():
            raise ValidationError('Utente "{utente}" non è un operatore per ente [{ente}]'.format(
                utente=self.utente,
                ente=self.qualifica_ufficio.ufficio.ente,
            ))

    # OVERRIDE
    def save(self, *args, **kwargs):
        self._check_user_is_op()
        super().save(*args, **kwargs)  # Call the "real" save() method.



class Token(models.Model):
    """
    An access token that is associated with a user.
    This is essentially the same as the token model from Django REST Framework
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE, null=True)

    expires = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

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
