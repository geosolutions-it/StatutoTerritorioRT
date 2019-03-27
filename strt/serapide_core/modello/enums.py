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

TIPOLOGIA_RISORSA = {
    'delibera': {
        'label': 'Delibera di avvio ',
        'tooltip': 'ai sensi dell’articolo. 17 L.R. 65/2014'
    },
    'tipo_risorsa_2': {
        'label': 'testo label',
        'tooltip': 'testo tooltip'
    }
}

TIPOLOGIA_CONTATTO = Choices(
        ('unknown', _('UNKNOWN')),
        ('generico', _('GENERICO')),
        ('acvas', _('AUT_COMP_VAS')),
        ('sca', _('SOGGETTO_SCA')),
        ('ente', _('ENTE')),
        ('genio_civile', _('GENIO_CIVILE')),
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
        ('procedimento_semplificato', _('PROCEDIMENTO_SEMPLIFICATO')),
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
        ('creato_piano', _('Creato Piano/Variante')),  # Comune
        # Procedura VAS
        ('richiesta_verifica_vas', _('Documento Preliminare VAS')),  # AC
        ('pareri_verifica_sca', _('Pareri verifica VAS')),  # SCA
        ('emissione_provvedimento_verifica', _('Emissione Provvedimento di verifica')),  # AC
        ('pubblicazione_provvedimento_verifica', _('Pubblicazione provvedimento di verifica')),  # AC/Comune
        ('avvio_consultazioni_sca', _('Avvio consultazioni SCA')),  # Comune/AC
        ('pareri_sca', _('Pareri SCA')),  # SCA
        ('avvio_esame_pareri_sca', _('Avvio esame pareri SCA')),  # Comune
        ('upload_elaborati_vas', _('Upload elaborati VAS')),  # Comune
        # Avvio
        ('avvio_procedimento', _('Avvio del Procedimento')),  # Comune
        ('formazione_del_piano', _('Formazione del Piano')),  # Comune
        ('protocollo_genio_civile', _('Protocollo Genio Civile')),  # Comune
        ('protocollo_genio_civile_id', _('Protocollo N.')),  # Genio Civile
        ('richiesta_conferenza_copianificazione', _('Convocazione conferenza di copianificazione')),  # Comune
        ('convocazione_conferenza_copianificazione', _('Convocazione conferenza di copianificazione')),  # Regione
        # Adozione
        ('osservazioni_enti', _('Osservazioni Enti')),  # Enti
        ('osservazioni_regione', _('Osservazioni Regione')),  # Regione
        ('upload_osservazioni_privati', _('Upload Osservazioni Privati')),  # Comune
    )

TOOLTIP_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        # Procedura VAS
        ('richiesta_verifica_vas', _('art 23  L.R. 10/2010')),
        ('emissione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        ('pubblicazione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        ('avvio_consultazioni_sca', _('art.22  L.R. 10/2010')),
        ('emissione_provvedimento_verifica', _('art 22  L.R. 10/2010')),
        ('pubblicazione_provvedimento_verifica', _('art 22  L.R. 10/2010')),
        # Avvio
        ('avvio_procedimento', _('art. 17 L.R. 65/2014, comma 1, art. 21 Disciplina del Piano , PIT-PPR')),
        ('richiesta_conferenza_copianificazione', _('art.25 L.R. 65/2014')),
        ('convocazione_conferenza_copianificazione', _('art.25 L.R. 65/2014')),
    )

TIPOLOGIA_ATTORE = Choices(
        ('unknown', _('UNKNOWN')),
        ('comune', _('Comune')),
        ('regione', _('Regione')),
        ('ac', _('AC')),
        ('sca', _('SCA')),
        ('enti', _('ENTI')),
        ('genio_civile', _('GENIO_CIVILE')),
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
