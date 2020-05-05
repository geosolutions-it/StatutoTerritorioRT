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

from serapide_core.modello.models import (
    SoggettoOperante,
    ParereVAS,
    ConsultazioneVAS,
    ParereVerificaVAS
)

from serapide_core.modello.enums import (
    Fase,
    TipologiaVAS,
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


# @rules.predicate
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


# @rules.predicate
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


# @rules.predicate
def procedura_vas_is_valid(piano, procedura_vas=None):
    if procedura_vas == None:
        procedura_vas = piano.procedura_vas

    if procedura_vas.piano == piano:
        # Perform checks specifically for the current "Fase"
        if piano.fase == Fase.DRAFT:
            if procedura_vas.tipologia == TipologiaVAS.SEMPLIFICATA:
                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.VAS_SEMPLIFICATA.value, archiviata=False)
                if risorse.all().count() == 1:
                    risorsa = procedura_vas.risorse.get(tipo=TipoRisorsa.VAS_SEMPLIFICATA.value, archiviata=False)
                    if risorsa.dimensione > 0 and \
                            risorsa.file and \
                            os.path.exists(risorsa.file.path):
                        return True, []
                return False, ['Risorsa mancante per VAS semplificata']

            elif procedura_vas.tipologia == TipologiaVAS.VERIFICA:
                msg = []

                if SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).count() == 0:
                    msg.append("Soggetto AC mancante")
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).count() == 0:
                    msg.append("Soggetto SCA mancante")

                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.VAS_VERIFICA.value, archiviata=False)
                if risorse.all().count() > 0:
                    for r in risorse:
                        if r.dimensione == 0 or not r.file or not os.path.exists(r.file.path):
                            msg.append('Errore nella risorsa VAS verifica [{}]'.format(r))
                else:
                    msg.append('Risorsa mancante per VAS verifica')
                return len(msg) == 0, msg
             
            elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO:
                msg = []

                if SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).count() == 0:
                    msg.append("Soggetto AC mancante")
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).count() == 0:
                    msg.append("Soggetto SCA mancante")
                    
                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.DOCUMENTO_PRELIMINARE_VAS_SEMPLIFICATO.value, archiviata=False)
                if risorse.all().count() > 0:
                    for r in risorse:
                        if r.dimensione == 0 or not r.file or not os.path.exists(r.file.path):
                            msg.append('Errore nella risorsa VAS proceimento semplificato [{}]'.format(r))
                else:
                    msg.append('Risorsa mancante per VAS proceimento semplificato')
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO:
                msg = []
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).count() == 0:
                    msg.append("Soggetto AC mancante")
                if SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).count() == 0:
                    msg.append("Soggetto SCA mancante")
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
                return True, []
            else:
                return False, ['Tipologia VAS sconosciuta [{}]'.format(procedura_vas.tipologia)]

        elif piano.fase.nome == Fase.ANAGRAFICA:
            if procedura_vas.tipologia == TipologiaVAS.SEMPLIFICATA:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia in [TipologiaVAS.VERIFICA, TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO]:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
                return True
            else:
                return False
    return False
