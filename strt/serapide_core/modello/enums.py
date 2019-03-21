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

from model_utils import Choices
from django.utils.translation import gettext as _


FASE = Choices(
        ('unknown', _('UNKNOWN')),
        ('draft', _('DRAFT')),
        ('anagrafica', _('ANAGRAFICA')),
        ('avvio', _('AVVIO')),
        ('adozione', _('ADOZIONE')),
        ('approvazione', _('APPROVAZIONE')),
        ('pubblicazione', _('PUBBLICAZIONE')),
    )

FASE_NEXT = {
    'unknown': None,
    'draft': FASE.anagrafica,
    'anagrafica': FASE.avvio,
    'avvio': FASE.adozione,
    'adozione': FASE.approvazione,
    'approvazione': FASE.pubblicazione,
    'pubblicazione': None
}

TIPOLOGIA_CONTATTO = Choices(
        ('unknown', _('UNKNOWN')),
        ('generico', _('GENERICO')),
        ('acvas', _('AUT_COMP_VAS')),
        ('sca', _('SOGGETTO_SCA')),
    )

TIPOLOGIA_PIANO = Choices(
        ('unknown', _('UNKNOWN')),
        ('operativo', _('OPERATIVO')),
        ('strutturale', _('STRUTTURALE')),
        ('variante', _('VARIANTE')),
    )

TIPOLOGIA_VAS = Choices(
        ('unknown', _('UNKNOWN')),
        ('semplificata', _('SEMPLIFICATA')),
        ('verifica', _('VERIFICA')),
        ('procedimento', _('PROCEDIMENTO')),
        ('non_necessaria', _('NON_NECESSARIA')),
    )

TIPOLOGIA_CONF_COPIANIFIZAZIONE = Choices(
        ('necessaria', _('NECESSARIA')),
        ('posticipata', _('POSTICIPATA')),
        ('non_necessaria', _('NON_NECESSARIA')),
    )

STATO_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        ('nessuna', _('NESSUNA')),
        ('attesa', _('ATTESA')),
        ('necessaria', _('NECESSARIA')),
    )

TIPOLOGIA_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        ('creato_piano', _('Creato Piano')),  # Comune
        ('richiesta_verifica_vas', _('Richiesta Verifica VAS')),  # AC
        ('avvio_procedimento', _('Avvio Procedimento')),  # Comune
        ('formazione_del_piano', _('Formazione del Piano')),  # Comune
        ('protocollo_genio_civile', _('Protocollo Genio Civile')),  # Genio Civile
        ('pareri_verifica_sca', _('Pareri Verifica VAS')),  # SCA
        ('osservazioni_enti', _('Osservazioni Enti')),  # SCA
        ('osservazioni_regione', _('Osservazioni Regione')),  # Regione
        ('upload_osservazioni_privati', _('Upload Osservazioni Privati')),  # Comune
        ('convocazione_conferenza_copianificazione', _('Convocazione Conferenza di Copianificazione')),  # Regione
        ('emissione_provvedimento_verifica', _('Emissione Provvedimento di Verifica')),  # AC
        ('pubblicazione_provvedimento_verifica', _('Pubblicazione Provvedimento di Verifica')),  # AC/Comune
        ('avvio_consultazioni_sca', _('Avvio Consultazioni SCA')),  # Comune
        ('pareri_sca', _('Pareri SCA')),  # SCA
        ('avvio_esame_pareri_sca', _('Avvio Esame Pareri SCA')),  # Comune
        ('upload_elaborati_vas', _('Upload Elaborati VAS')),  # Comune
    )

TIPOLOGIA_ATTORE = Choices(
        ('unknown', _('UNKNOWN')),
        ('comune', _('Comune')),
        ('regione', _('Regione')),
        ('ac', _('AC')),
        ('sca', _('SCA')),
        ('enti', _('ENTI')),
        ('genio_civile', _('Genio Civile')),
    )

AZIONI_BASE = {
    FASE.draft: [
        {
            "tipologia": TIPOLOGIA_AZIONE.creato_piano,
            "attore": TIPOLOGIA_ATTORE.comune
        },
        {
            "tipologia": TIPOLOGIA_AZIONE.richiesta_verifica_vas,
            "attore": TIPOLOGIA_ATTORE.comune
        }
    ],
    FASE.anagrafica: [
        {
            "tipologia": TIPOLOGIA_AZIONE.avvio_procedimento,
            "attore": TIPOLOGIA_ATTORE.comune
        }
    ]
    # FASE.avvio: [
    #     {
    #         "tipologia": TIPOLOGIA_AZIONE.formazione_del_piano,
    #         "attore": TIPOLOGIA_ATTORE.comune
    #     },
    #     {
    #         "tipologia": TIPOLOGIA_AZIONE.protocollo_genio_civile,
    #         "attore": TIPOLOGIA_ATTORE.genio_civile
    #     }
    # ]
}
