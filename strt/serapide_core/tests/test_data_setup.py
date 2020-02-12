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

import logging

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

logger = logging.getLogger(__name__)


class DataLoader:
    IPA_RT = 'r_toscan'
    IPA_FI = 'c_d612'
    IPA_LU = 'c_e715'
    IPA_PI = 'c_g702'

    enti_stored = {}
    utenti_stored = {}
    uffici_stored = {}

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

    FC_ADMIN =    'RSSMRA80A01D612Y'
    FC_INACTIVE = 'PLARSS85A15E715G'
    FC_ACTIVE1 =  'ACTIVE11A15E715G'
    FC_ACTIVE2 =  'ACTIVE22A15E715G'

    utenti = [
        {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'fiscal_code': FC_ADMIN,
        },
        {
            'first_name': 'Pinco',
            'last_name': 'Storto',
            'fiscal_code': FC_INACTIVE
        },
        {
            'first_name': 'Fiorenzo',
            'last_name': 'Fiorentino',
            'fiscal_code': FC_ACTIVE1
        },
        {
            'fiscal_code': FC_ACTIVE2
        },
    ]

    @classmethod
    def loadData(cls):

        for ente in cls.enti:
            ipa = ente['ipa']
            ente_db, created = Ente._default_manager.get_or_create(**ente)
            if not created:
                raise Exception("Could not create ENTE {}".format(ente))
            else:
                logger.warning("ENTE CREATO {}".format(ente_db))

            cls.enti_stored[ipa] = ente_db

            cls.uffici_stored[ipa] = []
            for ufficio in cls.uffici[ipa]:
                ufficio['ente'] = ente_db
                # logger.warning("CREATING UFFICIO {}".format(ufficio))
                uff_db,created = Ufficio._default_manager.get_or_create(**ufficio)
                if not created:
                    raise Exception("Could not create UFFICIO {}".format(ufficio))
                else:
                    logger.warning("UFFICIO CREATO {}".format(uff_db))

                cls.uffici_stored[ipa].append(uff_db)

        for user in cls.utenti:
            logger.warning("CREATING USER {}".format(user))
            user['password'] = '42'
            utente_db = Utente.objects.create_user(user['fiscal_code'], password=user['password'])
            # utente_db = Utente.objects.get_or_create(**user)
            cls.utenti_stored[user['fiscal_code']] = utente_db
            logger.warning("UTENTE CREATO {}".format(utente_db))

        utenti = Utente.objects.all()
        logger.warning("#UTENTI: {}".format(len(utenti) if utenti else 0))
        for u in utenti:
            logger.warning("UTENTE: {}".format(u))

        profili_to_store = [
            (cls.FC_ACTIVE1, Profilo.ADMIN_ENTE, DataLoader.IPA_FI),
            (cls.FC_ACTIVE1, Profilo.OPERATORE, DataLoader.IPA_FI),
            (cls.FC_ACTIVE1, Profilo.OPERATORE, DataLoader.IPA_LU),
            (cls.FC_ACTIVE2, Profilo.OPERATORE, DataLoader.IPA_FI),
            (cls.FC_ACTIVE2, Profilo.OPERATORE, DataLoader.IPA_LU),
        ]

        for cf, profilo, ipa in profili_to_store:
            pu = ProfiloUtente()
            pu.utente = cls.utenti_stored[cf]
            pu.profilo = profilo
            pu.ente = cls.enti_stored[ipa] if ipa else None
            pu.save()

        qu_stored = {}
        qu_to_store = [
            (DataLoader.IPA_FI, 0, [Qualifica.AC, Qualifica.RESP, Qualifica.SCA], {
                cls.FC_ACTIVE1: [Qualifica.AC, Qualifica.RESP],
                cls.FC_ACTIVE2: [Qualifica.AC, Qualifica.SCA],
            }),
            (DataLoader.IPA_FI, 1, [Qualifica.AC], {
                cls.FC_ACTIVE1: [Qualifica.AC],
            }),
            (DataLoader.IPA_LU, 0, [Qualifica.AC, Qualifica.SCA], {
                cls.FC_ACTIVE1: [Qualifica.SCA],
                cls.FC_ACTIVE2: [Qualifica.SCA],
            }),
        ]

        for ipa, idx_uff, qlist, userquals in qu_to_store:
            qu_stored[ipa] = {}

            for q in qlist:
                qu = QualificaUfficio()
                qu.ufficio = cls.uffici_stored[ipa][idx_uff]
                qu.qualifica = q
                qu.save()
                qu_stored[ipa][q] = qu
                logger.warning("STORED QU {} id:{}".format(qu, qu.id))
            for cf, qlist in userquals.items():
                for q in qlist:
                    ass = Assegnatario()
                    ass.utente = cls.utenti_stored[cf]
                    ass.qualifica_ufficio = qu_stored[ipa][q]
                    ass.save()
                    logger.warning("STORED ASSEGNATARIO: {} id:{}".format(ass, ass.id))


        # for q in [Qualifica.AC, Qualifica.RESP]:
        #     ass = Assegnatario()
        #     ass.utente = cls.utenti_stored[cls.FC_ACTIVE1]
        #     ass.qualifica_ufficio = qu_stored[IPA_FI][q]
        #     ass.save()
        #     logger.warning("STORING ASSEGNATARIO: {} id:{}".format(ass,ass.id))


        prof_loaded = ProfiloUtente.objects.all()
        for a in prof_loaded:
            logger.warning("LOADED PU: {} : id:{}".format(a, a.id))

        qu_loaded = QualificaUfficio.objects.all()
        for a in qu_loaded:
            logger.warning("LOADED QU: {} : id:{}".format(a, a.id))

        assegnatari = Assegnatario.objects\
            .filter(utente__fiscal_code=cls.FC_ACTIVE1)
        for a in assegnatari:
            logger.warning("LOADED ASSEGNATARIO: {} : id:{}".format(a, a.id))


