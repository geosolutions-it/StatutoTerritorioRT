# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import logging
import rules

from strt_users.enums import (
    Profilo, Qualifica,
    Priv, QualificaRichiesta)

from strt_users.models import (
    Utente,
    ProfiloUtente,
    Assegnatario,
    QualificaUfficio,
    Ente)

from serapide_core.modello.models import (
    Piano,
    SoggettoOperante,
    Delega,
    # PianoAuthTokens
)

logger = logging.getLogger(__name__)

# ############################################################################ #
# User
# ############################################################################ #

def is_recognizable(user):
    # logger.warning("is_recognizable: USER {user} {anon} {act} {auth}".format(user=user, anon=user.is_anonymous, act=user.is_active, auth=user.is_authenticated))
    return user \
           and not user.is_anonymous \
           and user.is_active \
           and user.is_authenticated

def can_create_piano(utente, ente):
    if not isinstance(utente, Utente):
        logger.error('Utente di tipo errato <{tipo}>[{utente}]'.format(tipo=type(utente), utente=utente))
        return False

    profili_utente = ProfiloUtente.objects\
        .filter(utente=utente, ente=ente)

    for pu in profili_utente:
        p = pu.profilo
        if Priv.CREATE_PLAN in p.get_priv():
            return True

    return False

def has_profile(utente, p:Profilo):
    return ProfiloUtente.objects \
        .filter(utente=utente, profilo=p) \
        .exists()

def can_edit_piano(utente, ente):
    if not isinstance(utente, Utente):
        logger.error('Utente di tipo errato <{tipo}>[{utente}]'.format(tipo=type(utente), utente=utente))
        return False

    profili_utente = ProfiloUtente.objects\
        .filter(utente=utente, ente=ente)

    for pu in profili_utente:
        p = pu.profilo
        if Priv.OPERATE_PLAN in p.get_priv():
            return True

    return False

def has_qualifica(utente, ente:Ente, qualifica:Qualifica):
    return Assegnatario.objects. \
        filter(utente=utente). \
        filter(qualifica_ufficio__qualifica=qualifica). \
        filter(qualifica_ufficio__ufficio__ente=ente). \
        exists()

def is_soggetto_operante(utente, piano:Piano, qualifica:Qualifica=None, qualifica_richiesta:QualificaRichiesta=None):
    # TODO aggiungere gestione deleghe
    logger.warning("is_soggetto_operante: USER {utente}".format(utente=utente))
    assegnatario = Assegnatario.objects.filter(utente=utente)
    if qualifica:
        assegnatario = assegnatario.filter(qualifica_ufficio__qualifica=qualifica)
    qu_set = [a.qualifica_ufficio for a in assegnatario]
    # if len(qu_set) == 0: # shortcut
    #     return False
    logger.warning("qu_set {}".format(qu_set))

    qs =  SoggettoOperante.objects. \
        filter(piano=piano). \
        filter(qualifica_ufficio__in=qu_set)

    logger.warning("SOps {}".format(qs))

    if qualifica:
        qs = qs.filter(qualifica_ufficio__qualifica=qualifica)

    if qualifica_richiesta:
        qs = qs.filter(qualifica_ufficio__qualifica__in=qualifica_richiesta.qualifiche())

    return qs.exists()

def is_soggetto_proponente(utente, piano:Piano):

    return Assegnatario.objects. \
        filter(utente=utente). \
        filter(qualifica_ufficio=piano.soggetto_proponente). \
        exists()

def is_soggetto(utente, piano:Piano):
    return is_soggetto_operante(utente, piano) or \
           is_soggetto_proponente(utente, piano) or \
           has_qualifica(utente, piano.ente, Qualifica.RESP)

@rules.predicate
def can_access_piano(user, piano):
    _has_access = any(
        m.organization == piano.ente
        for m in user.memberships
    )

    if not _has_access:
        _tokens = Delega.objects.filter(user=user)
        for _t in _tokens:
            if not _t.is_expired():
                _allowed_pianos = [_pt.piano for _pt in PianoAuthTokens.objects.filter(token__key=_t.key)]
                _has_access = piano in _allowed_pianos
                if _has_access:
                    break
    return _has_access


@rules.predicate
def is_actor_for_token(token, actor):
    return True
    # _attore = None
    # if token and \
    # (isinstance(token, str) or isinstance(token, Delega):
    #     token = Delega.objects.get(key=token)
    #     _attore = Contatto.attore(token.user, token=token.key)
    #
    # if _attore is None:
    #     return False
    # else:
    #     return (_attore.lower() == actor.lower())


# @rules.predicate
# def is_actor_for_role(user_info, actor):
#     _user = user_info[0]
#     _role = user_info[1]
#     _attore = None
#     if _user and \
#     _role and not isinstance(_role, Ente):
#         _attore = Referente.attore(_user, role=_role)
#
#     if _attore is None:
#         return False
#     else:
#         return (_attore.lower() == actor.lower())


# TODO
# @rules.predicate
# def is_actor_for_organization(user_info, actor):
#     _user = user_info[0]
#     _organization = user_info[1]
#     _attore = None
#     if _user and \
#     _organization and isinstance(_organization, Ente):
#         _attore = Referente.attore(_user, organization=_organization.code)
#
#     if _attore is None:
#         return False
#     else:
#         return (_attore == actor)

def get_piani_visibili_id(utente:Utente):
    # TODO aggiungere gestione deleghe
    assegnatario = Assegnatario.objects.filter(utente=utente)
    qu_set = [a.qualifica_ufficio for a in assegnatario]
    logger.warning("qu_set {}".format(qu_set))

    qs =  SoggettoOperante.objects. \
        filter(qualifica_ufficio__in=qu_set)

    # piani per i quali l'utente è soggetto operante
    id_piani = {so.piano.id for so in qs.all()}

    # piani per i quali enti l'utente è RESP
    ass_resp =  Assegnatario.objects.filter(utente=utente, qualifica_ufficio__qualifica=Qualifica.RESP)
    enti_resp = { ass.qualifica_ufficio.ufficio.ente for ass in ass_resp}
    piani_resp = Piano.objects.filter(ente__in=enti_resp)
    id_piani |= {p.id for p in piani_resp}

    # TODO: piani accessibile da token

    return id_piani

