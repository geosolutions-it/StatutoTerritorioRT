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

from enum import Enum

from django.utils.translation import gettext as _
from model_utils import Choices

logger = logging.getLogger(__name__)

class Priv(Enum):
    ADMIN_USER = 'ADMIN_USER'
    CREATE_PLAN = 'CREATE_PLAN'
    MANAGE_PLAN = 'MANAGE_PLAN'
    OPERATE_PLAN = 'OPERATE_PLAN'

    @classmethod
    def create_choices(cls):
        return (
            (Priv.ADMIN_USER, _('Amministrazione utenti')),
            (Priv.CREATE_PLAN, _('Creazione piani')),
            (Priv.MANAGE_PLAN, _('Amministrazione piani')),
            (Priv.OPERATE_PLAN, _('Gestione piani')),
        )


class Profilo(Enum):
    ADMIN_PORTALE = 'ADMIN_PORTALE'
    RESP_RUP = 'RESP_RUP'
    ADMIN_ENTE = 'ADMIN_ENTE'
    OPERATORE = 'OPERATORE'

    @classmethod
    def create_choices(cls):
        # return Choices (
        #     (Profilo.ADMIN_PORTALE, _('Amministratore portale')),
        #     (Profilo.RESP_RUP, _('Responsabile RUP')),
        #     (Profilo.ADMIN_ENTE, _('Amministratore Ente')),
        #     (Profilo.OPERATORE, _('Operatore')),
        # )
        # return Choices (
        #     Profilo.ADMIN_PORTALE,
        #     Profilo.RESP_RUP,
        #     Profilo.ADMIN_ENTE,
        #     Profilo.OPERATORE,
        # )

        return  [(tag, _(tag.value)) for tag in cls]

    @classmethod
    def fix_enum(cls, obj):
        return fix_enum(cls, obj)

    def equal(self, obj):
        if self == obj:
            return True
        if self.name == obj:
            logger.warning('EQUAL on enum is string: {}'.format(obj) )
            return True
        if 'Profilo.' + self.name == obj:
            logger.warning('EQUAL on enum is string: {}'.format(obj) )
            return True

        return False

    def get_priv(self):
        '''
        :return: a list of related Privs
        '''

        return PRIV_BY_PROFILE[self]

PRIV_BY_PROFILE = {
    Profilo.ADMIN_PORTALE:
        [Priv.ADMIN_USER],
    Profilo.RESP_RUP:
        [Priv.ADMIN_USER],
    Profilo.ADMIN_ENTE:
        [Priv.OPERATE_PLAN, Priv.MANAGE_PLAN, Priv.CREATE_PLAN],
    Profilo.OPERATORE:
        [Priv.OPERATE_PLAN]
}

# def _(s):
#     return s;

# class Qualifica(models.TextChoices): # DJANGO 3
#     RUP = 'RUP', _('Responsabile Unico del Provvedimento')
#     AC = 'AC', _('AUT_COMP_VAS')
#     SCA = 'SCA', _('SOGGETTO_SCA')
#     GC = 'GC', _('Genio Civile')
#     PIAN = 'PIAN', _('Responsabile Pianificazione')
#     URB = 'URB', _('Responsabile Urbanistica')
#     GUEST = 'GUEST', _('Guest')

class TipoEnte(Enum):
    COMUNE = 'COMUNE'
    REGIONE = 'REGIONE'
    ALTRO = 'ALTRO'

    @classmethod
    def create_choices(cls):
        return  [(tag, _(tag.value)) for tag in cls]

    @classmethod
    def fix_enum(cls, obj):
        return fix_enum(cls, obj)


class Qualifica(Enum):
    RESP = 'RESP'
    AC = 'AC'
    SCA = 'SCA'
    GC = 'GC'
    PIAN = 'PIANIFICAZIONE'
    URB = 'URBANISTICA'
    READONLY = 'READONLY'

    @classmethod
    def create_choices(cls):
        return  [(tag, _(tag.value)) for tag in cls]

        # return Choices(
        #     Qualifica.RESP,
        #     Qualifica.AC,
        #     Qualifica.SCA,
        #     Qualifica.GC,
        #     Qualifica.PIAN,
        #     Qualifica.URB,
        #     Qualifica.READONLY,
        # )
        # def create_choices(self=None):
        #     return Choices(
        #         (Qualifica.RESP , _('Responsabile Comunale')),
        #         (Qualifica.AC, _('AUT_COMP_VAS')),
        #         (Qualifica.SCA, _('SOGGETTO_SCA')),
        #         (Qualifica.GC, _('Genio Civile')),
        #         (Qualifica.PIAN, _('Responsabile Pianificazione')),
        #         (Qualifica.URB, _('Responsabile Urbanistica')),
        #         (Qualifica.READONLY, _('Read-only')),
        #     )

    def is_allowed(self, tipo:TipoEnte):
        return tipo in ALLOWED_QUALIFICA_BY_TIPOENTE[self]

    @classmethod
    def fix_enum(cls, obj):
        return fix_enum(cls, obj)


ALLOWED_QUALIFICA_BY_TIPOENTE = {
    Qualifica.RESP: [TipoEnte.COMUNE],
    Qualifica.AC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.SCA: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.GC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.PIAN: [TipoEnte.REGIONE],
    Qualifica.URB: [TipoEnte.REGIONE],
    Qualifica.READONLY: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
}

class QualificaRichiesta(Enum):
    COMUNE = 'COMUNE'
    AC = 'AC'
    SCA = 'SCA'
    GC = 'GC'
    PIAN = 'PIAN'
    URB = 'URB'
    REGIONE = 'REGIONE'

    @classmethod
    def create_choices(cls):
        return Choices(
            (QualificaRichiesta.COMUNE , _('Responsabile Comunale')),
            (QualificaRichiesta.AC, _('VAS')),
            (QualificaRichiesta.SCA, _('SCA')),
            (QualificaRichiesta.GC, _('Genio Civile')),
            (QualificaRichiesta.PIAN, _('Responsabile Pianificazione')),
            (QualificaRichiesta.URB, _('Responsabile Urbanistica')),
            (QualificaRichiesta.REGIONE, _('Responsabile regionale')),
        )

    @classmethod
    def fix_enum(cls, obj):
        fix_enum(cls, obj)

    def is_ok(self, qual:Qualifica):
        return qual in ALLOWED_QUALIFICA_BY_RICHIESTA[self]

ALLOWED_QUALIFICA_BY_RICHIESTA = {
    QualificaRichiesta.COMUNE: [Qualifica.RESP],
    QualificaRichiesta.AC: [Qualifica.AC],
    QualificaRichiesta.SCA: [Qualifica.SCA],
    QualificaRichiesta.GC: [Qualifica.GC],
    QualificaRichiesta.PIAN: [Qualifica.PIAN],
    QualificaRichiesta.URB: [Qualifica.URB],
    QualificaRichiesta.REGIONE: [Qualifica.PIAN, Qualifica.PIAN],
}


def fix_enum(cls, obj):
    # logger.warning('fix_enum {}::{}'.format(cls.__name__, obj))
    if obj == None:
        return obj
    if isinstance(obj, cls):
        return obj
    if isinstance(obj, str):
        try:
            ret = cls[obj]
            logger.warning('Fixed 1 {}::{}'.format(cls, obj))
            return ret
        except KeyError:
            try:
                if obj.startswith(cls.__name__ + '.'):
                    key = obj[len(cls.__name__) + 1::]
                    ret = cls[key]
                    logger.warning('Fixed 2 {}::{}'.format(cls, key))
                    return ret
            except KeyError:
                pass

    logger.warning('Could not fix {}::{}'.format(cls, obj))
    return obj
