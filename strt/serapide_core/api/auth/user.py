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


def has_profile(utente, p:Profilo=None):
    qs = ProfiloUtente.objects.filter(utente=utente)
    if p:
        qs = qs.filter(profilo=p)
    return qs.exists()


# def can_edit_piano(utente, ente):
#     if not isinstance(utente, Utente):
#         logger.error('Utente di tipo errato <{tipo}>[{utente}]'.format(tipo=type(utente), utente=utente))
#         return False
#
#     profili_utente = ProfiloUtente.objects\
#         .filter(utente=utente, ente=ente)
#
#     for pu in profili_utente:
#         p = pu.profilo
#         if Priv.OPERATE_PLAN in p.get_priv():
#             return True
#
#     return False


def get_assegnamenti(utente, ente:Ente, qualifica:Qualifica):

    return Assegnatario.objects. \
        filter(utente=utente). \
        filter(qualifica_ufficio__qualifica=qualifica). \
        filter(qualifica_ufficio__ufficio__ente=ente)


def has_qualifica(utente, ente:Ente, qualifica:Qualifica):
    # TODO aggiungere check token

    return get_assegnamenti(utente, ente, qualifica).exists()


def get_so(utente, piano: Piano, qualifica: Qualifica = None):
    assegnatario = Assegnatario.objects.filter(utente=utente)
    if qualifica:
        assegnatario = assegnatario.filter(qualifica_ufficio__qualifica=qualifica)
    qu_set = [a.qualifica_ufficio for a in assegnatario]

    qs = SoggettoOperante.objects. \
        filter(piano=piano). \
        filter(qualifica_ufficio__in=qu_set)

    if qualifica:
        qs = qs.filter(qualifica_ufficio__qualifica=qualifica)

    return qs


def is_soggetto_operante(utente, piano: Piano, qualifica: Qualifica=None, qualifica_richiesta: QualificaRichiesta=None):

    qs = get_so(utente, piano, qualifica)

    if qualifica_richiesta:
        qs = qs.filter(qualifica_ufficio__qualifica__in=qualifica_richiesta.qualifiche())

    return qs.exists()


def is_soggetto_proponente(utente, piano:Piano):

    return Assegnatario.objects. \
        filter(utente=utente). \
        filter(qualifica_ufficio=piano.soggetto_proponente). \
        exists()


def can_access_piano(utente: Utente, piano: Piano):

    # responsabile di ente ok
    if has_qualifica(utente, piano.ente, Qualifica.RESP):
        return True

    # soggetto ok
    if is_soggetto_operante(utente, piano) or \
       is_soggetto_proponente(utente, piano):
        return True

    # abilitato tramite token ok
    return Delega.objects\
        .filter(
            token__user=utente,
            delegante__piano=piano)\
        .exists()


def can_edit_piano(utente: Utente, piano: Piano, q):

    qualifica = None
    qualifica_richiesta = None

    if isinstance(q, Qualifica):
        qualifica = q
    elif isinstance(q, QualificaRichiesta):
        qualifica_richiesta = q
    else:
        raise Exception("Qualifica inattesa [{}]".format(q))

    if qualifica == Qualifica.RESP or qualifica_richiesta == QualificaRichiesta.COMUNE:
        return has_qualifica(utente, piano.ente, Qualifica.RESP)

    # cerca fra i soggetti operanti
    qs = get_so(utente, piano, qualifica)

    if qualifica_richiesta:
        qs = qs.filter(qualifica_ufficio__qualifica__in=qualifica_richiesta.qualifiche())

    if qs.exists():
        return True

    # cerca deleghe
    qs = Delega.objects\
        .filter(
            token__user=utente,
            delegante__piano=piano)
    if qualifica:
        qs.filter(qualifica=qualifica)
    elif qualifica_richiesta:
        qs.filter(qualifica__in=qualifica_richiesta.qualifiche())

    return qs.exists()


def get_piani_visibili_id(utente: Utente):
    assegnatario = Assegnatario.objects.filter(utente=utente)
    qu_set = [a.qualifica_ufficio for a in assegnatario]
    # logger.warning("qu_set {}".format(qu_set))

    qs =  SoggettoOperante.objects. \
        filter(qualifica_ufficio__in=qu_set)

    # piani per i quali l'utente è soggetto operante
    id_piani = {so.piano.id for so in qs.all()}

    # piani per i quali enti l'utente è RESP
    ass_resp = Assegnatario.objects.filter(utente=utente, qualifica_ufficio__qualifica=Qualifica.RESP)
    enti_resp = { ass.qualifica_ufficio.ufficio.ente for ass in ass_resp}
    piani_resp = Piano.objects.filter(ente__in=enti_resp)
    id_piani |= {p.id for p in piani_resp}

    deleghe = Delega.objects.filter(token__user=utente)
    id_piani |= {d.delegante.piano.id for d in deleghe}

    return id_piani


def can_admin_delega(utente: Utente, delega: Delega):
    piano = delega.delegante.piano
    return has_qualifica(utente, piano.ente, Qualifica.RESP) or \
        Assegnatario.objects\
        .filter(qualifica_ufficio=delega.delegante.qualifica_ufficio, utente=utente)\
        .exists()
