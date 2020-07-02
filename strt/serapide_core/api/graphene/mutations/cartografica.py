# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2020, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import logging

from serapide_core.api.piano_utils import (
    crea_azione,
    riapri_azione,
)

from serapide_core.modello.models import (
    Piano,
    Azione,
    LottoCartografico,
    ElaboratoCartografico,
)

from serapide_core.modello.enums import (
    StatoAzione,
    TipologiaAzione,
)
from serapide_core.tasks import esegui_procedura_cartografica

from strt_users.enums import QualificaRichiesta

logger = logging.getLogger(__name__)


def inizializza_procedura_cartografica(piano: Piano, tipo: TipologiaAzione, parent: Azione):

    azione_carto = piano.getFirstAction(tipo)

    # Le azioni di controllo cartografico possono fallire: in quel caso l'azione precedente viene resa nuovamente
    # eseguibile. Una volta che l'azione parent è nuovamente eseguita, non creeremo una nuova azione cartografica,
    # ma useremo quella precedentemente creata

    if azione_carto:
        riapri_azione(azione_carto)
    else:
        azione_carto = crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.validazione_cartografia_adozione,
                qualifica_richiesta=QualificaRichiesta.AUTO,
                stato=StatoAzione.NECESSARIA,
            ))

    lotto = LottoCartografico.objects.filter(azione=azione_carto).first()
    if lotto:
        ElaboratoCartografico.objects.filter(lotto=lotto).delete()
    else:
        lotto = LottoCartografico(
            piano=piano,
            azione=azione_carto,
            azione_parent=parent
        )
        lotto.save()

    esegui_procedura_cartografica.delay(lotto.id)
