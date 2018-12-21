#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.test import TestCase
from django.contrib.auth import authenticate
from django.forms import ValidationError
from django.conf import settings
from strt_users.models import *
import jwt


# TEST AUTHENTICATION
# 1 - Responsabile ISIDE user
# 2 - SERAPIDE user
#   2.1 - Inactive SERAPIDE user
#   2.2 - Active SERAPIDE user

# TEST AUTHORIZATION RULES
# 1 - User can access to the private area?
#   1.1 - Is visible the user toolbar?
# 2 - User can manage accounts?
# 3 - User can access to SERAPIDE?


class UsersAuthenticationTests(TestCase):

    organizations = [
        {
            'code': 'RT',
            'name': 'Toscana',
            'type': {
                'code': 'R',
                'name': 'Regione'
            }
        },
        {
            'code': 'FI',
            'name': 'Firenze',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        },
        {
            'code': 'LU',
            'name': 'Lucca',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        },
        {
            'code': 'PI',
            'name': 'Pisa',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        }
    ]

    membership_types = [
        {
            'code': 'RUP',
            'name': 'Responsabile Unico del Procedimento',
            'org_type': 'C'
        },
        {
            'code': 'RUP',
            'name': 'Responsabile Unico del Procedimento',
            'org_type': 'R'
        },
        {
            'code': 'IVAS',
            'name': 'Ispettore VAS',
            'org_type': 'R'
        },
        {
            'code': 'IPIT',
            'name': 'Ispettore PIT',
            'org_type': 'R'
        },
        {
            'code': 'OP',
            'name': 'Operatore',
            'org_type': 'C'
        },
        {
            'code': 'RI',
            'name': 'Responsabile ISIDE',
            'org_type': 'C'
        },
        {
            'code': 'RI',
            'name': 'Responsabile ISIDE',
            'org_type': 'R'
        }
    ]

    Responsabile_ISIDE_user_data = {
        'first_name': 'Mario',
        'last_name': 'Rossi',
        'fiscal_code': 'RSSMRA80A01D612Y',
        'membership_type': 'RI',
        'organizations': [
            {
                'organization': 'RT'
            },
            {
                'organization': 'LU'
            }
        ]
    }

    inactive_SERAPIDE_user_data = {
        # 'first_name': 'Paolo',
        # 'last_name': 'Rossi',
        'fiscal_code': 'PLARSS85A15E715G'
    }

    active_SERAPIDE_user_data = {
        # 'first_name': 'Carlo',
        # 'last_name': 'Rossi',
        'fiscal_code': 'CRLRSS85A15E715G'
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for org in cls.organizations:
            org_type, created = OrganizationType._default_manager.get_or_create(
                code=org['type']['code'],
                name=org['type']['name'],
            )
            Organization._default_manager.get_or_create(
                code=org['code'],
                name=org['name'],
                type=org_type
            )
        for mt in cls.membership_types:
            membership_type, created = MembershipType._default_manager.get_or_create(
                code=mt['code'],
                organization_type=org_type
            )
            if created:
                membership_type.name = mt["name"]
                membership_type.description = f'{mt["name"]} per l\'ente {org_type.name}'
                membership_type.save()
        AppUser.objects.create(
            fiscal_code=cls.inactive_SERAPIDE_user_data['fiscal_code']
        )
        # Active SERAPIDE user
        active_SERAPIDE_user = AppUser.objects.create(
            fiscal_code=cls.active_SERAPIDE_user_data['fiscal_code']
        )
        UserMembership._default_manager.get_or_create(
            name='RUP Regione Toscana',
            member=active_SERAPIDE_user,
            organization=Organization.objects.get(
                code='RT'
            ),
            type=MembershipType.objects.get(
                code='RUP'
            ),
        )

    def test_Responsabile_ISIDE_user_auth(self):
        """
        Test Responsabile ISIDE authentication
        """
        encoded_jwt = jwt.encode(
            payload=self.Responsabile_ISIDE_user_data,
            key=settings.SECRET_KEY,
            algorithm='HS256'
        )
        self.assertIsNotNone(authenticate(encoded_jwt))

    def test_inactive_SERAPIDE_user_auth(self):
        """
        Test inactive (users without roles assigned to) SERAPIDE user authentication
        """
        encoded_jwt = jwt.encode(
            payload=self.inactive_SERAPIDE_user_data,
            key=settings.SECRET_KEY,
            algorithm='HS256'
        )
        self.assertRaises(ValidationError, lambda: authenticate(encoded_jwt))

    def test_active_SERAPIDE_user_auth(self):
        """
        Test active (users with roles assigned to) SERAPIDE user authentication
        """
        encoded_jwt = jwt.encode(
            payload=self.active_SERAPIDE_user_data,
            key=settings.SECRET_KEY,
            algorithm='HS256'
        )
        self.assertIsNotNone(authenticate(encoded_jwt))


# class UsersAuthorizationRulesTests(TestCase):
#
#     pass
