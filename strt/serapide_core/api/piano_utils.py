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

import datetime
import logging

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from serapide_core.modello.enums import (
    STATO_AZIONE, Fase, TipoExpire, TipoMail
)

from serapide_core.modello.models import (
    Azione, Piano
)

from serapide_core.signals import piano_phase_changed


log = logging.getLogger(__name__)


def needs_execution(azione: Azione):
    return azione and azione.stato != STATO_AZIONE.nessuna


def is_executed(azione: Azione):
    return azione and azione.stato == STATO_AZIONE.nessuna


def ensure_fase(check: Fase, expected: Fase):
    if check != expected:
        raise Exception("Fase Piano incongruente con l'azione richiesta -- {}".format(check.name))


def chiudi_azione(azione: Azione, data=None, set_data=True):
    log.warning('Chiusura azione [{a}]:{qr} in piano [{p}]'
                .format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))
    azione.stato = STATO_AZIONE.nessuna
    if set_data:
        azione.data = data if data else get_now()
    azione.save()


def crea_azione(azione: Azione, send_mail: bool = True):
    log.warning('Creazione azione [{a}]:{qr} in piano [{p}]'
                .format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))
    if azione.order is None:
        _order = Azione.count_by_piano(azione.piano)
        azione.order = _order

    azione.save()

    if send_mail:
        piano_phase_changed.send(
            message_type=TipoMail.azione_generica.name,
            sender=Piano,
            piano=azione.piano,
            azione=azione,)


def get_scadenza(start_datetime: datetime.datetime, exp: TipoExpire):

    delta_days = getattr(settings, exp.name + '_EXPIRE_DAYS', exp.value)
    avvio_scadenza = start_datetime.date()
    scadenza = avvio_scadenza + datetime.timedelta(days=delta_days)

    return avvio_scadenza, scadenza


def chiudi_pendenti(piano: Piano, attesa=True, necessaria=True):
    # - Complete Current Actions
    _now = get_now()
    stati = []
    if attesa:
        stati.append(STATO_AZIONE.attesa)
    if necessaria:
        stati.append(STATO_AZIONE.necessaria)

    for azione in Azione.objects.filter(piano=piano, stato__in=stati):
        log.warning('Chiusura forzata azione pendente {n}:{q}[{s}]'.format(
            n=azione.tipologia, q=azione.qualifica_richiesta.name, s=azione.stato))
        chiudi_azione(azione, data=_now)


def get_now():
    return datetime.datetime.now(timezone.get_current_timezone())
