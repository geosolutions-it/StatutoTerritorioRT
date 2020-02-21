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

class SerapideEnum(Enum):

    @classmethod
    def create_choices(cls):
        return  [(tag, _(tag.value)) for tag in cls]

    @classmethod
    def fix_enum(cls, obj, none_on_error=False):
        return fix_enum(cls, obj, none_on_error)

    def equal(self, obj):
        if self == obj:
            return True
        if self.name == obj:
            logger.warning('EQUAL on enum is string: {}'.format(obj) )
            return True
        if type(self).__name__ + '.' + self.name == obj:
            logger.warning('EQUAL on enum is string: {}'.format(obj) )
            return True

        return False


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


class Profilo(SerapideEnum):
    ADMIN_PORTALE = 'ADMIN_PORTALE'
    RESP_RUP = 'RESP_RUP'
    ADMIN_ENTE = 'ADMIN_ENTE'
    OPERATORE = 'OPERATORE'

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

class TipoEnte(SerapideEnum):
    COMUNE = 'COMUNE'
    REGIONE = 'REGIONE'
    ALTRO = 'ALTRO'


class Qualifica(SerapideEnum):
    RESP = 'RESP'
    AC = 'AC'
    SCA = 'SCA'
    GC = 'GC'
    PIAN = 'PIANIFICAZIONE'
    URB = 'URBANISTICA'
    READONLY = 'READONLY'

    def is_allowed(self, tipo:TipoEnte):
        return tipo in ALLOWED_QUALIFICA_BY_TIPOENTE[self]


ALLOWED_QUALIFICA_BY_TIPOENTE = {
    Qualifica.RESP: [TipoEnte.COMUNE],
    Qualifica.AC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.SCA: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.GC: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
    Qualifica.PIAN: [TipoEnte.REGIONE],
    Qualifica.URB: [TipoEnte.REGIONE],
    Qualifica.READONLY: [TipoEnte.COMUNE, TipoEnte.REGIONE, TipoEnte.ALTRO],
}

class QualificaRichiesta(SerapideEnum):
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


def fix_enum(cls, obj, none_on_error=False):
    # logger.warning('fix_enum {}::{}'.format(cls.__name__, obj))
    if obj is None:
        return obj
    if isinstance(obj, cls):
        return obj

    cls_name = cls.__name__

    if isinstance(obj, str):
        try:
            ret = cls[obj]
            logger.warning('Fixed 1 {}[{}]'.format(cls_name, obj))
            return ret
        except KeyError:
            try:
                if obj.startswith(cls_name + '.'):
                    key = obj[len(cls_name) + 1::]
                    ret = cls[key]
                    logger.warning('Fixed 2 {}[{}]'.format(cls_name, key))
                    return ret
            except KeyError:
                pass

            ret = [e for e in cls if
                   e.name.lower() == obj.lower() or (cls_name + '.' + e.name).lower() == obj.lower()]

            if len(ret) == 1:
                logger.warning('Fixed 3 {}[{}]'.format(cls_name, ret[0].name))
                return ret[0]
            elif len(ret) > 1:
                logger.warning('The lenient fixing procedure returned too many values - class {} key {}'.format(cls_name, obj))

    logger.warning('Could not fix {}[{}]'.format(cls_name, obj))
    return None if none_on_error else obj
