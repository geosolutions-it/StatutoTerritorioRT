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

from serapide_core.modello.enums import (
    FASE,
    TIPOLOGIA_VAS
)


# ############################################################################ #
# Procedura VAS
# ############################################################################ #
@rules.predicate
def procedura_vas_is_valid(piano, procedura_vas):
    if procedura_vas.piano == piano:
        if piano.fase.nome == FASE.draft:
            if procedura_vas.tipologia == TIPOLOGIA_VAS.semplificata:
                if procedura_vas.risorse.filter(tipo='vas_semplificata').count() == 1 and \
                    procedura_vas.risorse.get(tipo='vas_semplificata').dimensione > 0 and \
                        procedura_vas.risorse.get(tipo='vas_semplificata').file and \
                            os.path.exists(procedura_vas.risorse.get(tipo='vas_semplificata').file.path):
                                return True
                return False
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.verifica:
                if procedura_vas.risorse.filter(tipo='vas_verifica').count() > 0:
                    return procedura_vas.risorse.filter(tipo='vas_verifica').count() > 0 and \
                        all(
                            r.dimensione > 0 and r.file and os.path.exists(r.file.path)
                            for r in procedura_vas.risorse.filter(tipo='vas_verifica')
                        )
                return False
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.procedimento:
                return (
                    piano.autorita_competente_vas.count() > 0 and \
                        piano.soggetti_sca.count() > 0
                )
            elif procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                return True
            else:
                return False
    return False
