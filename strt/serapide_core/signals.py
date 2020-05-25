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

from serapide_core.modello.enums import TipoMail, TipologiaAzione
from serapide_core.modello.models import SoggettoOperante, Piano, Azione
from strt_users.models import Assegnatario, Ufficio, Utente
from .api.auth.user import get_UffAssTok

from .notifications_helper import send_now_notification

# from serapide_core.modello.models import PianoAuthTokens

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

        send_now_notification(users,
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


def get_destinatari_da_azione(azione: Azione, piano: Piano):
    qr = azione.qualifica_richiesta
    q = qr.qualifiche()

    uffici, utenti_assegnatari, token = get_UffAssTok(piano, azione.qualifica_richiesta)

    return uff2dest(uffici) + \
           utenti2dest(utenti_assegnatari) + \
           token2dest(token)


def get_destinatari_da_tipomail(notification_type, piano):
    return []  # TODO


def get_destinatari_da_piano(piano):
    return []  # TODO


def piano_phase_changed_notification(sender, **kwargs):

    logger.info("========== piano_phase_changed_notification")
    #logger.warning(kwargs, stack_info=True)

    if 'piano' in kwargs:
        notification_type = kwargs.get('message_type', None)
        azione = kwargs.get('azione', None)
        from_user = kwargs.get('user', None)
        piano = kwargs['piano']

        mail_args = {
            "user": from_user,
            "piano": piano,
        }

        if azione and isinstance(azione, Azione):
            utenti = get_destinatari_da_azione(azione, piano)

            mail_args['azione'] = azione
            mail_args['azione_tipo_name'] = azione.tipologia.name
            mail_args['azione_tipo_label'] = azione.tipologia.value
            mail_args['azione_scadenza'] = azione.scadenza
            notification_type = 'azione_generica'  # il nome del template

        elif notification_type and isinstance(notification_type, TipoMail):
            utenti = get_destinatari_da_tipomail(notification_type, piano)
            notification_type = notification_type.name

        else:
            logger.warning('Mail non tipizzata [{}]'.format(notification_type))
            # non sappiamo cosa sia, inviamo a tutti
            utenti = get_destinatari_da_piano(piano)

        for u in utenti:
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
        send_now_notification(
            utenti,
            # [ass.utente for ass in ass_list],
            notification_type,
            mail_args
            # {
            #   "user": from_user,
            #   "piano": piano,
            #   "tokens": tokens
            # }
        )
