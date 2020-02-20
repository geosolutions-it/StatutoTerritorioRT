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

import os
import rules

from serapide_core.modello.models import (
    SoggettoOperante,
    ParereVAS,
    ConsultazioneVAS,
    ParereVerificaVAS
)

from serapide_core.modello.enums import (
    Fase,
    TIPOLOGIA_VAS,
    TIPOLOGIA_AZIONE,
    TipoRisorsa
)

from serapide_core.modello.models import (
    Piano, Azione
)


# ############################################################################ #
# Procedura VAS
# ############################################################################ #
from strt_users.enums import Qualifica


@rules.predicate
def parere_sca_ok(user, procedura_vas):
    if user and procedura_vas:
        _piano = procedura_vas.piano
        _resources = procedura_vas.risorse.filter(tipo=TipoRisorsa.PARERE_SCA.value, archiviata=False, user=user)
        _consultazione_vas = ConsultazioneVAS.objects\
            .filter(procedura_vas=procedura_vas)\
            .order_by('data_creazione')\
            .first()
        _avvio_consultazioni_sca_count = Azione.count_by_piano(_piano, TIPOLOGIA_AZIONE.avvio_consultazioni_sca)
        _pareri_vas = ParereVAS.objects\
            .filter(
                user=user,
                inviata=True,
                procedura_vas=procedura_vas,
                consultazione_vas=_consultazione_vas,
            )
        if _resources and _resources.count() > 0 and \
        _pareri_vas and _pareri_vas.count() == _avvio_consultazioni_sca_count:
            return False
        else:
            return True
    return False


@rules.predicate
def parere_verifica_vas_ok(user, procedura_vas):
    if user and procedura_vas:
        _resources = procedura_vas.risorse.filter(tipo=TipoRisorsa.PARERE_VERIFICA_VAS.value, archiviata=False, user=user)
        _pareri_vas = ParereVerificaVAS.objects\
            .filter(
                user=user,
                inviata=True,
                procedura_vas=procedura_vas
            )
        if _resources and _resources.count() > 0 and \
        _pareri_vas and _pareri_vas.count() == 1:
            return False
        else:
            return True
    return False


@rules.predicate
def procedura_vas_is_valid(piano, procedura_vas=None):
    if procedura_vas == None:
        procedura_vas = piano.procedura_vas

    if procedura_vas.piano == piano:
        # Perform checks specifically for the current "Fase"
        if piano.fase == Fase.DRAFT:
            if procedura_vas.tipologia == TIPOLOGIA_VAS.semplificata:
                if procedura_vas.risorse.filter(tipo='vas_semplificata', archiviata=False).count() == 1 and \
                    procedura_vas.risorse.get(tipo='vas_semplificata', archiviata=False).dimensione > 0 and \
                    procedura_vas.risorse.get(tipo='vas_semplificata', archiviata=False).file and \
                    os.path.exists(procedura_vas.risorse.get(tipo='vas_semplificata', archiviata=False).file.path):
                        return True, []
                return False, ['Risorsa mancante per VAS semplificata']

            elif procedura_vas.tipologia == TIPOLOGIA_VAS.verifica:
                if procedura_vas.risorse.filter(tipo='vas_verifica', archiviata=False).count() > 0:
                    if all(r.dimensione > 0 and r.file and os.path.exists(r.file.path)
                           for r in procedura_vas.risorse.filter(tipo='vas_verifica', archiviata=False)):
                        return True, []
                    else:
                        return False, ['Errore in una risorsa per VAS verifica']
                return False, ['Risorsa mancante per VAS verifica']

            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento_semplificato:
                msg = []
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).count() == 0:
                    msg.append("Soggetto AC mancante")
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).count() == 0:
                    msg.append("Soggetto SCA mancante")
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento:
                msg = []
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).count() == 0:
                    msg.append("Soggetto AC mancante")
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).count() == 0:
                    msg.append("Soggetto SCA mancante")
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                return True, []
            else:
                return False, ['Tipologia VAS sconosciuta']

        elif piano.fase.nome == Fase.ANAGRAFICA:
            if procedura_vas.tipologia == TIPOLOGIA_VAS.semplificata:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.verifica:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento_semplificato:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                return True
            else:
                return False
    return False
