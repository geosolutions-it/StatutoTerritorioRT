# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions SAS.
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
    'obiettivi_piano': {
        'label': 'Obiettivi del Piano',
        'tooltip': ''
    },
    'quadro_conoscitivo': {
        'label': 'Quadro Conoscitivo',
        'tooltip': 'art. 17, lett.b, L.R. 65/2014'
    },
    'programma_attivita': {
        'label': 'Programma delle attività di inforamazione ai cittadini',
        'tooltip': ''
    },
    'individuazione_garante_informazione': {
        'label': 'Individuazione del garante dell\'informazione',
        'tooltip': ''
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
        ('variante_operativo', _('VARIANTE_OPERATIVO')),
        ('variante_strutturale', _('VARIANTE_STRUTTURALE')),
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
        ('richiesta_integrazioni', _('Richiesta Integrazioni')),  # Regione
        ('integrazioni_richieste', _('Integrazioni Richieste')),  # Comune
        ('formazione_del_piano', _('Formazione del Piano')),  # Comune
        ('protocollo_genio_civile', _('Protocollo Genio Civile')),  # Comune
        ('protocollo_genio_civile_id', _('Protocollo N.')),  # Genio Civile
        ('richiesta_conferenza_copianificazione', _('Richiesta Conferenza di copianificazione')),  # Comune
        ('esito_conferenza_copianificazione', _('Esito conferenza di copianificazione')),  # Regione
        # Adozione
        ('trasmissione_adozione', _('Trasmissione Adozione')),  # Comune
        ('osservazioni_enti', _('Osservazioni Enti')),  # Enti
        ('osservazioni_regione', _('Osservazioni Regione')),  # Regione
        ('upload_osservazioni_privati', _('Upload Osservazioni Privati')),  # Comune
        ('controdeduzioni', _('Controdeduzioni')),  # Comune
        ('piano_controdedotto', _('Piano Controdedotto')),  # Comune
        ('esito_conferenza_paesaggistica', _('Esiti conferenza paesaggistica')),  # Regione
        ('rev_piano_post_cp', _('Revisione Piano post Conf. Paesaggistica')),  # Comune
        # Adozione VAS
        ('pareri_adozione_sca', _('Pareri SCA')),  # SCA
        ('parere_motivato_ac', _('Parere Motivato')),  # AC
        ('upload_elaborati_adozione_vas', _('Upload elaborati VAS')),  # Comune
        # Approvazione
        ('trasmissione_approvazione', _('Invio documentazione per Approvazione')),  # Comune
        ('attribuzione_conformita_pit', _('Attribuzione Conformità PIT')),  # Regione
        ('esito_conferenza_paesaggistica_ap', _('Convocazione CP')),  # Regione
        ('pubblicazione_approvazione', _('Pubblicazione Approvazione')),  # Comune
        # Pubblicazione
        ('convocazione_commissione_paritetica', _('Convocazione Commissione Paritetica')),  # Comune
        ('compilazione_finale_monitoraggio_urbanistico', _('Compilazione Finale Monitoraggio Urbanistico')),  # Comune
        ('pubblicazione_piano', _('Pubblicazione Piano')),  # Comune
    )

FASE_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        ('creato_piano', 'draft'),
        # Procedura VAS
        ('richiesta_verifica_vas', 'anagrafica'),
        ('pareri_verifica_sca', 'anagrafica'),
        ('emissione_provvedimento_verifica', 'anagrafica'),
        ('pubblicazione_provvedimento_verifica', 'anagrafica'),
        ('avvio_consultazioni_sca', 'anagrafica'),
        ('pareri_sca', 'anagrafica'),
        ('avvio_esame_pareri_sca', 'anagrafica'),
        ('upload_elaborati_vas', 'anagrafica'),
        # Avvio
        ('avvio_procedimento', 'anagrafica'),
        ('richiesta_integrazioni', 'anagrafica'),
        ('integrazioni_richieste', 'anagrafica'),
        ('formazione_del_piano', 'anagrafica'),
        ('protocollo_genio_civile', 'anagrafica'),
        ('protocollo_genio_civile_id', 'anagrafica'),
        ('richiesta_conferenza_copianificazione', 'anagrafica'),
        ('esito_conferenza_copianificazione', 'anagrafica'),
        # Adozione
        ('trasmissione_adozione', 'avvio'),
        ('osservazioni_enti', 'avvio'),
        ('osservazioni_regione', 'avvio'),
        ('upload_osservazioni_privati', 'avvio'),
        ('controdeduzioni', 'avvio'),
        ('piano_controdedotto', 'avvio'),
        ('esito_conferenza_paesaggistica', 'avvio'),
        ('rev_piano_post_cp', 'avvio'),
        # Adozione VAS
        ('pareri_adozione_sca', 'avvio'),
        ('parere_motivato_ac', 'avvio'),
        ('upload_elaborati_adozione_vas', 'avvio'),
        # Approvazione
        ('trasmissione_approvazione', 'adozione'),
        ('attribuzione_conformita_pit', 'adozione'),
        ('esito_conferenza_paesaggistica_ap', 'adozione'),
        ('pubblicazione_approvazione', 'adozione'),
        # Pubblicazione
        ('convocazione_commissione_paritetica', 'approvazione'),
        ('compilazione_finale_monitoraggio_urbanistico', 'approvazione'),
        ('pubblicazione_piano', 'approvazione'),
    )

TOOLTIP_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        # Procedura VAS
        ('richiesta_verifica_vas', _('art.23 L.R. 10/2010')),
        ('emissione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        ('pubblicazione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        ('avvio_consultazioni_sca', _('art.22 L.R. 10/2010')),
        ('emissione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        ('pubblicazione_provvedimento_verifica', _('art.22 L.R. 10/2010')),
        # Avvio
        ('avvio_procedimento', _('art. 17 L.R. 65/2014, comma 1, art. 21 Disciplina del Piano , PIT-PPR')),
        ('richiesta_conferenza_copianificazione', _('art.25 L.R. 65/2014')),
        ('protocollo_genio_civile', _('art.65/104 RR')),
        ('protocollo_genio_civile_id', _('art.65/104 RR')),
        ('esito_conferenza_copianificazione', _('art.25 L.R. 65/2014')),
        # Adozione
        ('trasmissione_adozione', _('art.19 L.R. 65/2014')),
        ('osservazioni_enti', _('art.19 L.R. 65/2014')),
        ('osservazioni_regione', _('art.19 L.R. 65/2014')),
        ('upload_osservazioni_privati', _('art.19 L.R. 65/2014')),
        ('controdeduzioni', _('art.19 L.R. 65/2014')),
        ('piano_controdedotto', _('art.19 L.R. 65/2014')),
        ('esito_conferenza_paesaggistica', _('art.19 L.R. 65/2014')),
        ('rev_piano_post_cp', _('art.19 L.R. 65/2014')),
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
    ],
    FASE.avvio: [
        {
            "tipologia": TIPOLOGIA_AZIONE.trasmissione_adozione,
            "attore": TIPOLOGIA_ATTORE.comune
        },
    ],
    FASE.adozione: [
        {
            "tipologia": TIPOLOGIA_AZIONE.trasmissione_approvazione,
            "attore": TIPOLOGIA_ATTORE.comune
        },
    ],
    FASE.approvazione: [
        # {
        #     "tipologia": TIPOLOGIA_AZIONE.convocazione_commissione_paritetica,
        #     "attore": TIPOLOGIA_ATTORE.comune
        # },
        # {
        #     "tipologia": TIPOLOGIA_AZIONE.compilazione_finale_monitoraggio_urbanistico,
        #     "attore": TIPOLOGIA_ATTORE.comune
        # },
        {
            "tipologia": TIPOLOGIA_AZIONE.pubblicazione_piano,
            "attore": TIPOLOGIA_ATTORE.comune
        },
    ]
}
