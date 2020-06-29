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
    StatoAzione, Fase, TipoExpire, TipoMail
)

from serapide_core.modello.models import (
    Azione, Piano, AzioneReport
)

import serapide_core.signals as signals
# from serapide_core.tasks import etj_test

log = logging.getLogger(__name__)


def needs_execution(azione: Azione):
    return azione and azione.stato in (StatoAzione.NECESSARIA, StatoAzione.ATTESA)


def is_executed(azione: Azione):
    return azione and azione.stato == StatoAzione.ESEGUITA


def ensure_fase(check: Fase, expected: Fase):
    if check != expected:
        raise Exception("Fase Piano incongruente con l'azione richiesta -- {}".format(check.name))


def chiudi_azione(azione: Azione, data=None, set_data=True, stato: StatoAzione = StatoAzione.ESEGUITA):
    if stato not in (StatoAzione.ESEGUITA, StatoAzione.FALLITA):
        raise Exception("Stato di chiusura non corretto -- {}".format(stato))

    log.info('Chiusura azione [{a}]:{qr} in piano [{p}] {fail}'
                .format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano,
                        fail=' FALLITA' if stato==StatoAzione.FALLITA else ''))
    azione.stato = stato
    if set_data:
        azione.data = data if data else get_now()
    azione.save()


def crea_azione(azione: Azione, send_mail: bool = True):
    log.info('Creazione azione [{a}]:{qr} in piano [{p}]'
                .format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))

    # q = etj_test.delay('Creazione azione [{a}]:{qr} in piano [{p}]'
    #             .format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))
    # log.warning("RES ---> {}".format( q.get()))

    if azione.order is None:
        _order = Azione.count_by_piano(azione.piano)
        azione.order = _order

    azione.save()

    if send_mail:
        responses = signals.piano_phase_changed.send_robust(
            sender=Piano,
            piano=azione.piano,
            azione=azione,)

        for r, resp in responses:
            if isinstance(resp, Exception):
                log.warning('*** Errore invio mail: {}'.format(resp))

    return azione


def riapri_azione(azione: Azione, send_mail: bool = True):

    log.info('Riapertura azione [{a}]:{qr} in piano [{p}]'.format(
             a=azione.tipologia,
             qr=azione.qualifica_richiesta,
             p=azione.piano))

    azione.stato = StatoAzione.NECESSARIA
    azione.data = None
    azione.save()

    AzioneReport.objects.filter(azione=azione).delete()

    if send_mail:
        responses = signals.piano_phase_changed.send_robust(
            sender=Piano,
            piano=azione.piano,
            azione=azione,)

        for r, resp in responses:
            if isinstance(resp, Exception):
                log.warning('*** Errore invio mail: {}'.format(resp))


def get_scadenza(start_datetime: datetime.datetime, exp: TipoExpire):

    delta_days = getattr(settings, exp.name + '_EXPIRE_DAYS', exp.value)
    avvio_scadenza = start_datetime.date()
    scadenza = avvio_scadenza + datetime.timedelta(days=delta_days)

    return avvio_scadenza, scadenza


def is_scaduta(azione: Azione):
    return azione.scadenza and azione.scadenza < get_now().date()


def chiudi_pendenti(piano: Piano, attesa=True, necessaria=True):
    # - Complete Current Actions
    _now = get_now()
    stati = []
    if attesa:
        stati.append(StatoAzione.ATTESA)
    if necessaria:
        stati.append(StatoAzione.NECESSARIA)

    for azione in Azione.objects.filter(piano=piano, stato__in=stati):
        log.warning('Chiusura forzata azione pendente {n}:{q}[{s}]'.format(
            n=azione.tipologia, q=azione.qualifica_richiesta.name, s=azione.stato))
        chiudi_azione(azione, data=_now)


def get_now():
    return datetime.datetime.now(timezone.get_current_timezone())
