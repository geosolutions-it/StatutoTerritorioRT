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

from .enums import (FASE,
                    TIPOLOGIA_PIANO)


log = logging.getLogger(__name__)


class Fase(models.Model):
    codice = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(
        choices=FASE,
        default=FASE.draft,
        max_length=20)
    descrizione = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "strt_core_fase"
        verbose_name_plural = 'Fasi'

    def __str__(self):
        return 'Fase: {} - {}'.format(self.codice, self.nome)


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
    data_delibera = models.DateTimeField(null=True, blank=True)
    data_creazione = models.DateTimeField(null=True, blank=True)
    data_accettazione = models.DateTimeField(null=True, blank=True)
    data_avvio = models.DateTimeField(null=True, blank=True)
    data_approvazione = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    fase = models.ForeignKey(Fase, related_name='piani_operativi', on_delete=models.CASCADE)
    storico_fasi = models.ManyToManyField(Fase, through='FasePianoStorico')

    class Meta:
        db_table = "strt_core_piano"
        verbose_name_plural = 'Piani'
        unique_together = (('nome', 'codice',),)

    def __str__(self):
        return 'Piano: {} - {}'.format(self.codice, self.nome)

    def post_save(self):
        _now = datetime.utcnow().replace(tzinfo=pytz.utc)
        _full_hist = list(self.storico_fasi.all())
        _prev_state = _full_hist[len(_full_hist) - 1] if len(_full_hist) > 0 else None
        if self.fase:
            if not _prev_state or _prev_state.codice != self.fase.codice:
                _state_hist = FasePianoStorico()
                _state_hist.piano = self
                _state_hist.fase = self.fase
                _state_hist.data_apertura = _now
                _state_hist.save()

                if _prev_state:
                    _state_hist = FasePianoStorico.objects.filter(piano=self, fase=_prev_state).first()
                    _state_hist.data_chiusura = _now
                    _state_hist.save()


class FasePianoStorico(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    data_apertura = models.DateTimeField()
    data_chiusura = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "strt_core_piano_storico_fasi"
