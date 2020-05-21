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
    ParereVerificaVAS
)

from serapide_core.modello.enums import (
    Fase,
    TipologiaVAS,
    TipologiaAzione,
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
            if procedura_vas.tipologia == TipologiaVAS.VERIFICA_SEMPLIFICATA:
                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.RELAZIONE_MOTIVATA.value, archiviata=False)
                if not risorse.all().exists():
                    return False, ['Risorsa mancante per VAS con verifica semplificata']
                elif risorse.all().count() == 1:
                    risorsa = procedura_vas.risorse.get(tipo=TipoRisorsa.RELAZIONE_MOTIVATA.value, archiviata=False)
                    if risorsa.dimensione > 0 and \
                            risorsa.file and \
                            os.path.exists(risorsa.file.path):
                        return True, []
                    else:
                        return False, ['Risorsa vuota per VAS con verifica semplificata']
                else:
                    return False, ['Troppe risorse relative a VAS con verifica semplificata']

            elif procedura_vas.tipologia == TipologiaVAS.VERIFICA:
                msg = []

                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).exists():
                    msg.append("Soggetto AC mancante")
                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).exists():
                    msg.append("Soggetto SCA mancante")

                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS.value, archiviata=False)
                if risorse.all().exists():
                    for r in risorse:
                        if r.dimensione == 0 or not r.file or not os.path.exists(r.file.path):
                            msg.append('Errore nella risorsa VAS verifica [{}]'.format(r))
                else:
                    msg.append('Risorsa mancante per VAS verifica')
                return len(msg) == 0, msg
             
            elif procedura_vas.tipologia == TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO:
                msg = []

                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).exists():
                    msg.append("Soggetto AC mancante")
                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).exists():
                    msg.append("Soggetto SCA mancante")
                    
                risorse = procedura_vas.risorse.filter(tipo=TipoRisorsa.DOCUMENTO_PRELIMINARE_VAS.value, archiviata=False)
                if risorse.all().count() > 0:
                    for r in risorse:
                        if r.dimensione == 0 or not r.file or not os.path.exists(r.file.path):
                            msg.append('Errore nella risorsa VAS procedimento semplificato [{}]'.format(r))
                else:
                    msg.append('Risorsa mancante per VAS proceimento semplificato')
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TipologiaVAS.PROCEDURA_ORDINARIA:
                msg = []
                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.AC).exists():
                    msg.append("Soggetto AC mancante")
                if not SoggettoOperante.get_by_qualifica(piano, Qualifica.SCA).exists():
                    msg.append("Soggetto SCA mancante")
                return len(msg) == 0, msg

            elif procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
                return True, []
            else:
                return False, ['Tipologia VAS sconosciuta [{}]'.format(procedura_vas.tipologia)]

        elif piano.fase.nome == Fase.ANAGRAFICA:
            if procedura_vas.tipologia == TipologiaVAS.VERIFICA_SEMPLIFICATA:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia in [TipologiaVAS.VERIFICA, TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO]:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TipologiaVAS.PROCEDURA_ORDINARIA:
                return procedura_vas.conclusa
            elif procedura_vas.tipologia == TipologiaVAS.NON_NECESSARIA:
                return True
            else:
                return False
    return False
