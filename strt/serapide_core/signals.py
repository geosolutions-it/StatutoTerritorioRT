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

from django.dispatch import Signal

from strt_users.enums import Qualifica
from serapide_core.modello.enums import TipoMail
from serapide_core.modello.models import Piano, Azione

import serapide_core.api.auth.user as auth_user

import serapide_core.notifications_helper as notifications_helper

logger = logging.getLogger(__name__)

# ############################################################################ #
# Signals
# ############################################################################ #
"""
e.g:
    message_sent = Signal(providing_args=["message", "thread", "reply"])
    ...
    message_sent.send(sender=cls, message=msg, thread=thread, reply=True)
"""
piano_phase_changed = Signal(providing_args=["user", "piano", ])


# ############################################################################ #
# Signal Handlers
# ############################################################################ #
def message_sent_notification(sender, **kwargs):

    if 'message' in kwargs:
        message = kwargs['message']
        thread = kwargs['thread']
        reply = kwargs['reply']
        users = [u for u in thread.users.all() if u != message.sender]

        notifications_helper.send_now_notification(users,
                              "message_sent",
                              {
                                "from_user": message.sender,
                                "message": message,
                                "thread": thread,
                                "reply": reply
                              })


def log(piano, notification_type, user_type, user):
    logger.info("SEND {piano}:{azione} TO {usertype} {user}".format(
        user=user,
        usertype=user_type,
        piano=piano.codice,
        azione=notification_type))


class MockUser:

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.email = None
        self.ufficio = None

    def __str__(self):
        return '"Ufficio: {uff}" <{mail}>'.format(uff=self.first_name, mail=self.email)


def uff2dest(uffici):
    ret = []
    for uff in uffici:
        mu = MockUser()
        mu.first_name = uff.nome
        mu.last_name = uff.ente.nome
        mu.email = uff.email
        mu.ufficio = uff

        ret.append(mu)

    return ret


def utenti2dest(utenti):
    ret = []
    for u in utenti:
        u.token = None  # aggiunge campo , altrimenti fallisce l'accesso
        ret.append(u)
    return ret


def token2dest(tokenlist):
    ret = []
    for token in tokenlist:
        u = token.user
        u.token = token
        ret.append(u)
    return ret


def get_destinatari_da_qualifiche(piano: Piano, qualifiche):
    uffici, utenti_assegnatari, token = auth_user.get_UffAssTok(piano, qualifiche)

    return uff2dest(uffici) + \
           utenti2dest(utenti_assegnatari) + \
           token2dest(token)


def get_destinatari_da_azione(piano: Piano, azione: Azione):
    return get_destinatari_da_qualifiche(piano, azione.qualifica_richiesta.qualifiche())


def get_destinatari_da_tipomail(piano: Piano, tipo: TipoMail):
    if tipo == TipoMail.trasmissione_dp_vas:
        return get_destinatari_da_qualifiche(piano, [Qualifica.AC])

    elif tipo == TipoMail.piano_phase_changed:
        return get_destinatari_da_qualifiche(piano, [Qualifica.AC, Qualifica.SCA, Qualifica.OPCOM, Qualifica.URB,
                                                     Qualifica.PIAN, Qualifica.GC])

    elif tipo == TipoMail.pubblicazione_piano:
        return get_destinatari_da_qualifiche(piano, [Qualifica.AC, Qualifica.SCA, Qualifica.OPCOM, Qualifica.URB,
                                                     Qualifica.PIAN, Qualifica.GC])
    else:
        logger.warning('*** TipoMail non gestito [{}]'.format(tipo))
        return []


def get_destinatari_da_piano(piano):
    return get_destinatari_da_qualifiche(piano, [Qualifica.AC, Qualifica.SCA, Qualifica.OPCOM, Qualifica.URB,
                                                 Qualifica.PIAN, Qualifica.GC])


# TODO: questo nome di funzione va cambiato dato che gestisce tutte le mail
def piano_phase_changed_notification(sender, **kwargs):

    # logger.info("========== piano_phase_changed_notification")
    # logger.warning(kwargs, stack_info=True)

    notification_type = kwargs.get('message_type', None)
    azione = kwargs.get('azione', None)
    from_user = kwargs.get('user', None)
    piano = kwargs.get('piano', None)

    mail_info = 'azione:{}'.format(azione.tipologia.name) if azione else 'tipo:{}'.format(notification_type)
    logger.info("========== GESTIONE INVIO MAIL piano:{} {}".format(piano.codice, mail_info))

    if not piano:
        logger.warning("Piano non definito, nessuna mail inviata")
        return

    mail_args = {
        "user": from_user,
        "piano": piano,
    }

    if azione and isinstance(azione, Azione):
        destinatari = get_destinatari_da_azione(piano, azione)

        mail_args['azione'] = azione
        mail_args['azione_tipo_name'] = azione.tipologia.name
        mail_args['azione_tipo_label'] = azione.tipologia.value
        mail_args['azione_scadenza'] = azione.scadenza
        notification_type = 'azione_generica'  # il nome del template

    elif notification_type and isinstance(notification_type, TipoMail):
        destinatari = get_destinatari_da_tipomail(piano, notification_type)
        notification_type = notification_type.name

    else:
        logger.warning('message_type non tipizzato [{}]'.format(notification_type))
        # non sappiamo cosa sia, inviamo a tutti
        destinatari = get_destinatari_da_piano(piano)

    from strt_users.models import Utente
    for u in destinatari:
        if isinstance(u, Utente):
            dest = '"{}" <{}>'.format(u.get_full_name(), u.email)
            tok = 'TOKEN {}'.format(u.token.key) if u.token else ''
        else:
            dest = u
            tok = ''

        logger.info("SENDING MAIL TO {to} - Piano {piano} - TEMPLATE {temp}{azione}{token}".format(
            to=dest,
            piano=piano.codice,
            temp=notification_type,
            azione=(' - AZIONE ' + azione.tipologia.name) if azione else '',
            token=tok
        ))

    # todo : check for uffici
    notifications_helper.send_now_notification(
        destinatari,
        notification_type,
        mail_args
        # {
        #   "user": from_user,
        #   "piano": piano,
        #   "tokens": tokens
        # }
    )
