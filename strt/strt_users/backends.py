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
from django.core.exceptions import ValidationError
from .models import (
    Organization, UserMembership, MembershipType
)
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


UserModel = get_user_model()


class StrtPortalAuthentication:

    def authenticate(self, data):
        with transaction.atomic():
            if 'user_role' in data and data['user_role'] in settings.RESPONSABILE_ISIDE_CODES:
                # If role is Responsabile ISIDE (RI) the user can be not already registered
                user, created = UserModel._default_manager.get_or_create(
                    fiscal_code=data['user_fiscal_code'].strip().upper(),
                    first_name=data['user_first_name'].strip().title(),
                    last_name=data['user_last_name'].strip().title()
                )
            else:
                # if no role provided then the user must have already been registered
                try:
                    user = UserModel._default_manager.get_by_natural_key(
                        data['user_fiscal_code'].strip().title()
                    )
                except UserModel.DoesNotExist:
                    raise ValidationError(_('L\'utente non risulta censito.'))
            if user:
                is_active = getattr(user, 'is_active', None)
                if not is_active:
                    # If user is recognized inactive it will be activated at the first access
                    user.is_active = True
                    user.save()
                if 'organizations' in data:
                    for organization in data['organizations']:
                        try:
                            # Organizations must be already registered
                            org = Organization._default_manager.get(
                                code=organization.strip()
                            )
                        except Organization.DoesNotExist:
                            raise ValidationError(_('L\'ente non risulta censito.'))
                        membership_type, created = MembershipType._default_manager.get_or_create(
                            code=f'RI{org.type.code}',
                            organization_type=org.type,
                            name=_(f'Responsabile ISIDE {org.type.name}'),
                            description=_(f'Responsabile ISIDE per l\'ente {org.type.name}')
                        )
                        UserMembership._default_manager.get_or_create(
                            name=_(f'Responsabile ISIDE {org.type.name} {org.name}'),
                            member=user,
                            organization=org,
                            type=membership_type,
                        )
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
