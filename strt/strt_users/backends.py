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

import jwt

from django import forms
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .models import (
    Token, Organization, UserMembership, MembershipType
)


UserModel = get_user_model()


class StrtPortalAuthentication:

    def authenticate(self, encoded_jwt, token=None):

        if token:
            """
            Try to find a user with the given token
            """
            try:
                t = Token.objects.get(key=token)

                if not t.is_expired() and self.user_can_authenticate(t.user):
                    return t.user
            except Token.DoesNotExist:
                return None

        if encoded_jwt:
            """
            Fall back to default behavior
            """
            payload = jwt.decode(
                jwt=encoded_jwt,
                key=settings.SECRET_KEY,
                algorithms='HS256'
            )

            with transaction.atomic():

                if len(payload['organizations']) != 1:
                    raise forms.ValidationError(_('Ente obbligatorio.'))

                _organization = payload['organizations'].pop()['organization'].strip()

                org = None
                try:
                    # Organizations must be already registered
                    org = Organization._default_manager.get(
                        code=_organization
                    )
                except Organization.DoesNotExist:
                    raise forms.ValidationError(
                        _("L'ente {} non risulta censito.".format(_organization))
                    )

                if 'fiscal_code' in payload and payload['fiscal_code']:

                    # Responsabile ISIDE user
                    if 'membership_type' in payload and payload['membership_type'] and \
                            payload['membership_type'] == settings.RESPONSABILE_ISIDE_CODE:

                        user, created = UserModel._default_manager.get_or_create(
                            fiscal_code=payload['fiscal_code'].strip().upper()
                        )
                        if created:
                            user.first_name = payload['first_name'].strip().title()
                            user.last_name = payload['last_name'].strip().title()
                            user.save()

                        membership_type, created = MembershipType._default_manager.get_or_create(
                            code=settings.RESPONSABILE_ISIDE_CODE,
                            organization_type=org.type
                        )
                        if created:
                            membership_type.name = _("Responsabile ISIDE {}".format(org.type.name)),
                            membership_type.description = _("Responsabile ISIDE per l'ente {}".format(org.type.name))
                            membership_type.save()
                        UserMembership._default_manager.get_or_create(
                            name=_("Responsabile ISIDE {} {}".format(org.type.name, org.name)),
                            member=user,
                            organization=org,
                            type=membership_type,
                        )

                    # SERAPIDE user
                    elif 'membership_type' not in payload or not payload['membership_type']:
                        try:
                            user = UserModel._default_manager.get_by_natural_key(
                                payload['fiscal_code'].strip().upper()
                            )
                            if not user.memberships or not user.memberships.filter(organization=org):
                                raise forms.ValidationError(_('All\'utente non risulta assegnato nessun ruolo.'))
                        except UserModel.DoesNotExist:
                            raise forms.ValidationError(_('L\'utente non risulta censito.'))

                    else:
                        raise forms.ValidationError(_('Ruolo non ammesso.'))

                # Errors
                else:
                    raise forms.ValidationError(_('Campo Codice Fiscale obbligatorio.'))

                if user:
                    is_active = getattr(user, 'is_active', None)
                    if not is_active:
                        # If user is recognized inactive it will be activated at the first access
                        user.is_active = True
                        user.save()
                    return user

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
