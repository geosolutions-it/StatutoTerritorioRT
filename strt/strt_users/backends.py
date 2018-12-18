#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.contrib.auth import get_user_model
from .models import (
    Organization, UserMembership, MembershipType
)
from django.db import transaction
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import jwt


UserModel = get_user_model()


class StrtPortalAuthentication:

    def authenticate(self, encoded_jwt):

        payload = jwt.decode(
            jwt=encoded_jwt,
            key=settings.SECRET_KEY,
            algorithms='HS256'
        )

        with transaction.atomic():

            if payload['fiscal_code']:

                # Responsabile ISIDE user
                if payload['membership_type'] and \
                        payload['membership_type'] == settings.RESPONSABILE_ISIDE_CODE:
                    user, created = UserModel._default_manager.get_or_create(
                        fiscal_code=payload['fiscal_code'].strip().upper()
                    )
                    if created:
                        user.first_name = payload['first_name'].strip().title()
                        user.last_name = payload['last_name'].strip().title()
                        user.save()
                    for o in payload['organizations']:
                        try:
                            # Organizations must be already registered
                            org = Organization._default_manager.get(
                                code=o['organization'].strip()
                            )
                        except Organization.DoesNotExist:
                            raise forms.ValidationError(
                                _(f'L\'ente {o["organization"].strip()} non risulta censito.')
                            )
                        membership_type, created = MembershipType._default_manager.get_or_create(
                            code=settings.RESPONSABILE_ISIDE_CODE,
                            organization_type=org.type
                        )
                        if created:
                            membership_type.name = _(f'Responsabile ISIDE {org.type.name}'),
                            membership_type.description = _(f'Responsabile ISIDE per l\'ente {org.type.name}')
                            membership_type.save()
                        UserMembership._default_manager.get_or_create(
                            name=_(f'Responsabile ISIDE {org.type.name} {org.name}'),
                            member=user,
                            organization=org,
                            type=membership_type,
                        )

                # SERAPIDE user
                elif not payload['membership_type']:
                    try:
                        user = UserModel._default_manager.get_by_natural_key(
                            payload['fiscal_code'].strip().upper()
                        )
                        if not user.memberships:
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
