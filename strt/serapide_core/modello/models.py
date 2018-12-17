# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import uuid
import logging
from datetime import datetime

import pytz
from django.db import models

from .enums import (STATUS,
                    TIPOLOGIA_PIANO)


log = logging.getLogger(__name__)


class Stato(models.Model):
    codice = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(
        choices=STATUS,
        default=STATUS.draft,
        max_length=20)
    descrizione = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Stati'

    def __str__(self):
        return 'Stato: {} - {}'.format(self.codice, self.nome)


class Piano(models.Model):
    """
    Every "Piano" in the serapide_core application has a unique uuid
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    nome = models.CharField(max_length=255, null=False, blank=False)
    codice = models.CharField(max_length=255, null=False, blank=False)
    identificativo = models.CharField(max_length=255)
    tipologia = models.CharField(
        choices=TIPOLOGIA_PIANO,
        default=TIPOLOGIA_PIANO.unknown,
        max_length=20)
    notes = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True, default='')
    data_creazione = models.DateTimeField(null=True, blank=True)
    data_accettazione = models.DateTimeField(null=True, blank=True)
    data_avvio = models.DateTimeField(null=True, blank=True)
    data_approvazione = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    stato = models.ForeignKey(Stato, related_name='piani_operativi', on_delete=models.CASCADE)
    storico_stati = models.ManyToManyField(Stato, through='StatoPianoStorico')

    class Meta:
        verbose_name_plural = 'Piani'
        unique_together = (('nome', 'codice',),)

    def __str__(self):
        return 'Piano: {} - {}'.format(self.codice, self.nome)

    def post_save(self):
        _now = datetime.utcnow().replace(tzinfo=pytz.utc)
        _full_hist = list(self.storico_stati.all())
        _prev_state = _full_hist[len(_full_hist) - 1] if len(_full_hist) > 0 else None
        if self.stato:
            if not _prev_state or _prev_state.codice != self.stato.codice:
                _state_hist = StatoPianoStorico()
                _state_hist.piano = self
                _state_hist.stato = self.stato
                _state_hist.data_apertura = _now
                _state_hist.save()

                if _prev_state:
                    _state_hist = StatoPianoStorico.objects.filter(piano=self, stato=_prev_state).first()
                    _state_hist.data_chiusura = _now
                    _state_hist.save()


class StatoPianoStorico(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    stato = models.ForeignKey(Stato, on_delete=models.CASCADE)
    data_apertura = models.DateTimeField()
    data_chiusura = models.DateTimeField(null=True, blank=True)
