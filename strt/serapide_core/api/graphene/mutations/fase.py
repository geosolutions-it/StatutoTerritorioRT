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
import datetime

from django.conf import settings

from django.utils import timezone

from serapide_core.modello.models import (
    Azione,
    AzioniPiano,
)

from serapide_core.modello.enums import (
    FASE,
    AZIONI_BASE,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_ATTORE,
)

logger = logging.getLogger(__name__)


def promuovi_piano(fase, piano):

    procedura_vas = piano.procedura_vas

    # Update Azioni Piano
    _order = piano.azioni.count()

    # - Attach Actions Templates for the Next "Fase"
    for _a in AZIONI_BASE[fase.nome]:
        _azione = Azione(
            tipologia=_a["tipologia"],
            attore=_a["attore"],
            order=_order,
            stato=STATO_AZIONE.necessaria
        )
        _azione.save()
        _order += 1
        AzioniPiano.objects.get_or_create(azione=_azione, piano=piano)

    # - Update Action state accordingly
    if fase.nome == FASE.anagrafica:
        _creato = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
        if _creato.stato != STATO_AZIONE.necessaria:
            raise Exception("Stato Inconsistente!")

        _creato.stato = STATO_AZIONE.nessuna
        _creato.data = datetime.datetime.now(timezone.get_current_timezone())
        _creato.save()

    elif fase.nome == FASE.avvio:
        _richiesta_integrazioni = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.richiesta_integrazioni).first()

        if _richiesta_integrazioni and _richiesta_integrazioni.stato != STATO_AZIONE.nessuna:
            _richiesta_integrazioni.stato = STATO_AZIONE.nessuna
            _richiesta_integrazioni.save()

        _integrazioni_richieste = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.integrazioni_richieste).first()

        if _integrazioni_richieste and _integrazioni_richieste.stato != STATO_AZIONE.nessuna:
            _integrazioni_richieste.stato = STATO_AZIONE.nessuna
            _integrazioni_richieste.save()
