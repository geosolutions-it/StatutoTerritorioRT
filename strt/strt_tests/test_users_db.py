# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2020, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from django.test import TestCase

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from strt_users.enums import (
    Profilo
)

from strt_users.models import (
    Ente,
    Ufficio,
    Qualifica,
    QualificaUfficio,
    Utente,
    ProfiloUtente,
    Assegnatario,
    TipoEnte
)

IPA_RT = 'r_toscan'
IPA_FI = 'c_d612'
IPA_LU = 'c_e715'
IPA_PI = 'c_g702'

class UsersDBTests(TestCase):

    enti_db = {}
    utenti_db = {}
    uffici_db = {}

    enti = [
        {
            'ipa': IPA_RT,
            'nome': 'Toscana',
            'tipo': TipoEnte.REGIONE
        },
        {
            'ipa': IPA_FI,
            'name': 'Firenze',
            'tipo': TipoEnte.COMUNE
        },
        {
            'ipa': IPA_LU,
            'name': 'Lucca',
            'tipo': TipoEnte.COMUNE
        },
        {
            'ipa': IPA_PI,
            'name': 'Pisa',
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

    FC_ADMIN = 'RSSMRA80A01D612Y'
    FC_INACTIVE = 'PLARSS85A15E715G'
    FC_ACTIVE1 = 'ACTIVE11A15E715G'
    FC_ACTIVE2 = 'ACTIVE22A15E715G'

    utenti = [
        {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'fiscal_code': FC_ADMIN,
        },
        {
            'fiscal_code': FC_INACTIVE
        },
        {
            'fiscal_code': FC_ACTIVE1
        },
        {
            'fiscal_code': FC_ACTIVE2
        },
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for ente in cls.enti:
            ipa = ente['ipa']
            ente_db, created = Ente._default_manager.get_or_create(ente)
            cls.enti_db[ipa] = ente_db

            cls.uffici_db[ipa] = []
            for ufficio in cls.uffici[ipa]:
                ufficio['ente'] = ente_db
                uff_db,created = Ufficio._default_manager.get_or_create(ufficio)
                cls.uffici_db[ipa].append(uff_db)

        for user in cls.utenti:
            utente_db,created = Utente._default_manager.get_or_create(user)
            cls.utenti_db[user['fiscal_code']] = utente_db


    def test_profile_admin(self):
        """
        """
        admin_profile = ProfiloUtente()
        admin_profile.utente = self.utenti_db[self.FC_ADMIN]
        admin_profile.profilo = Profilo.ADMIN_PORTALE
        admin_profile.ente = None

        admin_profile.save()


    def test_profile_checks(self):
        """
        """
        admin_profile = ProfiloUtente()
        admin_profile.utente = self.utenti_db[self.FC_ACTIVE1]

        admin_profile.profilo = Profilo.ADMIN_PORTALE
        admin_profile.ente = self.enti_db[IPA_PI]

        with transaction.atomic():
            try:
                admin_profile.save()
                self.fail("IntegrityError not detected")
            except IntegrityError as e:
                pass

        admin_profile.profilo = Profilo.ADMIN_ENTE
        admin_profile.ente = None

        with transaction.atomic():
            try:
                admin_profile.save()
                self.fail("IntegrityError not detected")
            except IntegrityError as e:
                pass

    def test_qualuff_checks(self):
        qu = QualificaUfficio()
        qu.ufficio = self.uffici_db[IPA_RT][0]
        qu.qualifica = Qualifica.RESP

        with transaction.atomic():
            try:
                qu.save()
                self.fail("IntegrityError not detected")
            except (IntegrityError, ValidationError) as e:
                pass

        qu.ufficio = self.uffici_db[IPA_FI][0]
        qu.qualifica = Qualifica.PIAN

        with transaction.atomic():
            try:
                qu.save()
                self.fail("IntegrityError not detected")
            except (IntegrityError, ValidationError) as e:
                pass
