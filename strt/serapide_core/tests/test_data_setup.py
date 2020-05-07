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

    UFF_GC_TN = "GENIO CIVILE TOSCANA NORD"
    UFF_GC_TS = "GENIO CIVILE TOSCANA SUD"
    UFF_GC_VC = "GENIO CIVILE TOSCANA VALDARNO CENTRALE"
    UFF_GC_VI = "GENIO CIVILE TOSCANA VALDARNO INFERIORE"
    UFF_GC_VS = "GENIO CIVILE TOSCANA VALDARNO SUPERIORE"
    UFF_PIAN  = "Uff Pianificazione"
    UFF1 = 'Ufficio 1'
    UFF2 = 'Ufficio 2'

    uffici = {
        IPA_RT: [
            {'nome': UFF1,'email': 'uff1@rt'},
            {'nome': UFF2,'email': 'uff2@rt'},
            UFF_GC_TN,
            UFF_GC_TS,
            UFF_GC_VC,
            UFF_GC_VI,
            UFF_GC_VS,
            UFF_PIAN
        ],
        IPA_FI: [
            {'nome': UFF1, 'email': 'uff1@fi'},
            {'nome': UFF2,'email': 'uff2@fi'}
        ],
        IPA_LU: [
            {'nome': UFF1,'email': 'uff1@lu'},
            {'nome': UFF2,'email': 'uff2@lu'}
        ],
        IPA_PI: [
            {'nome': UFF1, 'email': 'uff1@lu'},
        ]
    }

    FC_ADMIN =    'RSSMRA80A01D612Y'
    FC_INACTIVE = 'PLARSS85A15E715G'
    FC_RUP_RESP = 'ACTIVE11A15E715G'
    FC_ACTIVE2 =  'ACTIVE22A15E715G'
    FC_GC1     =  'GCGCGC22A15E715G'
    FC_AC1     =  'ACACAC22A15E715G'
    FC_SCA1    =  'SKASKA22A15E715G'
    FC_PIAN    =  'PIANRT22A15E715G'
    FC_DELEGATO = 'DELGAT22A15E715G'

    utenti = [
        {
            'first_name': 'Carlo',
            'last_name': 'Magno',
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
            'fiscal_code': FC_RUP_RESP
        },
        {
            'fiscal_code': FC_ACTIVE2
        },
        {
            'first_name': 'Genio',
            'last_name': 'Geniale',
            'fiscal_code': FC_GC1
        },
        {
            'first_name': 'Acacio',
            'last_name': 'Summaccheronio',
            'fiscal_code': FC_AC1
        },
        {
            'first_name': 'Scarolo',
            'last_name': 'Scacchiere',
            'fiscal_code': FC_SCA1
        },
        {
            'first_name': 'Pino',
            'last_name': 'Piano',
            'fiscal_code': FC_PIAN
        },
        {
            'first_name': 'Dele',
            'last_name': 'Gato',
            'fiscal_code': FC_DELEGATO
        },
    ]

    profili_to_store = [
        (FC_RUP_RESP, Profilo.ADMIN_ENTE, IPA_FI),
        (FC_RUP_RESP, Profilo.OPERATORE, IPA_FI),
        (FC_ACTIVE2, Profilo.OPERATORE, IPA_FI),
        (FC_ACTIVE2, Profilo.OPERATORE, IPA_LU),
        (FC_GC1, Profilo.OPERATORE, IPA_RT),
        (FC_PIAN, Profilo.OPERATORE, IPA_RT),
        (FC_AC1, Profilo.OPERATORE, IPA_PI),
        (FC_SCA1, Profilo.OPERATORE, IPA_LU),
    ]

    qu_to_store = [
        (IPA_FI, UFF1, [Qualifica.AC, Qualifica.OPCOM, Qualifica.SCA], {
            FC_RUP_RESP: [Qualifica.OPCOM],
            FC_ACTIVE2: [Qualifica.AC, Qualifica.SCA],
        }),
        (IPA_FI, UFF2, [Qualifica.AC], {
            #FC_RUP_RESP: [Qualifica.AC],
        }),
        (IPA_LU, UFF1, [Qualifica.SCA], {
            FC_ACTIVE2: [Qualifica.SCA],
            FC_SCA1: [Qualifica.SCA],
        }),
        (IPA_PI, UFF1, [Qualifica.AC], {
            # FC_RUP_RESP: [Qualifica.SCA],
            # FC_ACTIVE2: [Qualifica.AC],
            FC_AC1: [Qualifica.AC],
        }),
        (IPA_RT, UFF_GC_TN, [Qualifica.GC], {
            FC_GC1: [Qualifica.GC],
        }),
        (IPA_RT, UFF_PIAN, [Qualifica.PIAN], {
            FC_PIAN: [Qualifica.PIAN],
        }),
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

            cls.uffici_stored[ipa] = {}
            for uff in cls.uffici[ipa]:
                uff_dict = uff if isinstance(uff, dict) else {'nome':uff}
                uff_dict['ente'] = ente_db
                # logger.warning("CREATING UFFICIO {}".format(ufficio))
                uff_db,created = Ufficio._default_manager.get_or_create(**uff_dict)
                if not created:
                    raise Exception("Could not create UFFICIO {}".format(uff_dict))
                else:
                    logger.warning("UFFICIO CREATO {}".format(uff_db))

                cls.uffici_stored[ipa][uff_dict['nome']] = uff_db

        for user in cls.utenti:
            logger.warning("CREATING USER {}".format(user))
            user['password'] = '42'
            utente_db = Utente.objects.create_user(**user)
            # utente_db = Utente.objects.get_or_create(**user)
            cls.utenti_stored[user['fiscal_code']] = utente_db
            logger.warning("UTENTE CREATO {}".format(utente_db))

        utenti = Utente.objects.all()
        logger.warning("#UTENTI: {}".format(len(utenti) if utenti else 0))
        for u in utenti:
            logger.warning("UTENTE: {}".format(u))

        for cf, profilo, ipa in cls.profili_to_store:
            pu = ProfiloUtente()
            pu.utente = cls.utenti_stored[cf]
            pu.profilo = profilo
            pu.ente = cls.enti_stored[ipa] if ipa else None
            pu.save()

        qu_stored = {}

        for ipa, idx_uff, qlist, userquals in cls.qu_to_store:
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

        prof_loaded = ProfiloUtente.objects.all()
        for a in prof_loaded:
            logger.warning("LOADED PU: {} : id:{}".format(a, a.id))

        qu_loaded = QualificaUfficio.objects.all()
        for a in qu_loaded:
            logger.warning("LOADED QU: {} : id:{}".format(a, a.id))

        assegnatari = Assegnatario.objects\
            .filter(utente__fiscal_code=cls.FC_RUP_RESP)
        for a in assegnatari:
            logger.warning("LOADED ASSEGNATARIO: {} : id:{}".format(a, a.id))
