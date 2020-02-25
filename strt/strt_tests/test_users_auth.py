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
from fcntl import FD_CLOEXEC

from django.test import TestCase
from django.contrib.auth import authenticate
from django.forms import ValidationError
from django.conf import settings
from strt_users.managers import IsideUserManager

from strt_users.enums import (
    Profilo
)

from strt_users.models import (
    Ente,
    Ufficio,
    QualificaUfficio,
    Utente,
    ProfiloUtente,
    Assegnatario,
    TipoEnte
)
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

IPA_RT = 'r_toscanW'
IPA_FI = 'c_d612W'
IPA_LU = 'c_e715W'
IPA_PI = 'c_g702W'

class UsersAuthenticationTests:
    # class UsersAuthenticationTests(TestCase):

    enti_db = {}
    utenti_db = {}

    enti = [
        {
            'ipa': IPA_RT,
            'nome': 'Toscana',
            'tipo': TipoEnte.REGIONE
        },
        {
            'ipa': IPA_FI,
            'nome': 'Firenze',
            'tipo': TipoEnte.COMUNE
        },
        {
            'ipa': IPA_LU,
            'nome': 'Lucca',
            'tipo': TipoEnte.COMUNE
        },
        {
            'ipa': IPA_PI,
            'nome': 'Pisa',
            'tipo': TipoEnte.COMUNE
        }
    ]

    uffici = {
        IPA_RT: [
            {
                'nome': 'RT - ufficio 1',
                'email': 'uff1@rt'
            },
            {
                'nome': 'RT - ufficio 2',
                'email': 'uff2@rt'
            }
        ],
        IPA_FI: [
            {
                'nome': 'FI - ufficio 1',
                'email': 'uff1@fi'
            },
            {
                'nome': 'FI - ufficio 2',
                'email': 'uff2@fi'
            }
        ],
        IPA_LU: [
            {
                'nome': 'LU - ufficio 1',
                'email': 'uff1@lu'
            },
            {
                'nome': 'LU - ufficio 2',
                'email': 'uff2@lu'
            }
        ],
        IPA_PI: []
    }

    FC_ADMIN = 'RSSMRA80A01D612W'
    FC_INACTIVE = 'PLARSS85A15E715W'
    FC_ACTIVE = 'CRLRSS85A15E715W'

    Responsabile_ISIDE_user_data = {
        'first_name': 'Mario',
        'last_name': 'Rossi',
        'fiscal_code': FC_ADMIN,
        # 'membership_type': 'RI',
        # 'organizations': [
        #     {
        #         'organization': 'RT'
        #     },
        #     {
        #         'organization': 'LU'
        #     }
        # ]
    }

    inactive_SERAPIDE_user_data = {
        # 'first_name': 'Paolo',
        # 'last_name': 'Rossi',
        'fiscal_code': FC_INACTIVE
    }

    active_SERAPIDE_user_data = {
        # 'first_name': 'Carlo',
        # 'last_name': 'Rossi',
        'fiscal_code': FC_ACTIVE
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for ente in cls.enti:
            ipa = ente['ipa']
            ente_db, created = Ente._default_manager.get_or_create(**ente)
            cls.enti_db[ipa] = ente_db
            for ufficio in cls.uffici[ipa]:
                ufficio['ente'] = ente_db
                Ufficio._default_manager.get_or_create(**ufficio)

        # um = IsideUserManager()

        for user in [
                cls.Responsabile_ISIDE_user_data,
                cls.active_SERAPIDE_user_data,
                cls.inactive_SERAPIDE_user_data]:
            # um.create_user(
            #     fiscal_code=user['fiscal_code'],
            #     email=user['email'] if 'email' in user else None,
            #     extra_fields=user)
            utente_db,created = Utente._default_manager.get_or_create(**user)
            cls.utenti_db[user['fiscal_code']] = utente_db

        admin_profile = ProfiloUtente()
        admin_profile.utente = cls.utenti_db[cls.FC_ADMIN]
        admin_profile.profilo = Profilo.ADMIN_PORTALE
        admin_profile.ente = None

        admin_profile.save()

        # for mt in cls.membership_types:
        #     membership_type, created = MembershipType._default_manager.get_or_create(
        #         code=mt['code'],
        #         organization_type=org_type
        #     )
        #     if created:
        #         membership_type.name = mt["name"]
        #         membership_type.description = "{} per l'ente {}".format(mt["name"], org_type.name)
        #         membership_type.save()
        # AppUser.objects.create(
        #     fiscal_code=cls.inactive_SERAPIDE_user_data['fiscal_code']
        # )
        # # Active SERAPIDE user
        # active_SERAPIDE_user = AppUser.objects.create(
        #     fiscal_code=cls.active_SERAPIDE_user_data['fiscal_code']
        # )
        # UserMembership._default_manager.get_or_create(
        #     name='RUP Regione Toscana',
        #     member=active_SERAPIDE_user,
        #     organization=Organization.objects.get(
        #         code='RT'
        #     ),
        #     type=MembershipType.objects.get(
        #         code='RUP'
        #     ),
        # )

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
