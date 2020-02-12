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

    needsExecution,
    isExecuted,
    crea_azione,
    chiudi_azione,
)

from serapide_core.modello.enums import (
    Fase,
    AZIONI_BASE,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
    # TIPOLOGIA_ATTORE,
)


logger = logging.getLogger(__name__)


def promuovi_piano(fase, piano):

    procedura_vas = piano.procedura_vas

    # Update Azioni Piano
    _order = piano.azioni.count()

    # - Attach Actions Templates for the Next "Fase"
    for _a in AZIONI_BASE[fase]:

        crea_azione(piano,
                    Azione(
                        tipologia=_a["tipologia"],
                        qualifica_richiesta=_a["qualifica"],
                        order=_order,
                        stato=STATO_AZIONE.necessaria
                    ))
        _order += 1

    # - Update Action state accordingly
    if fase == Fase.ANAGRAFICA:
        _creato = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
        if _creato.stato != STATO_AZIONE.necessaria:
            raise Exception("Stato Inconsistente!")

        chiudi_azione(_creato)

    elif fase == Fase.AVVIO:
        _richiesta_integrazioni = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.richiesta_integrazioni).first()

        if needsExecution(_richiesta_integrazioni):
            chiudi_azione(_richiesta_integrazioni)

        _integrazioni_richieste = piano.azioni.filter(
                tipologia=TIPOLOGIA_AZIONE.integrazioni_richieste).first()

        if needsExecution(_integrazioni_richieste):
            chiudi_azione(_integrazioni_richieste)
