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

from enum import Enum

from model_utils import Choices

from django.utils.translation import gettext as _

from strt_users.enums import (
    QualificaRichiesta,
    SerapideEnum)


class Fase(SerapideEnum):
    UNKNOWN = 'UNKNOWN'
    DRAFT = 'DRAFT'
    ANAGRAFICA = 'ANAGRAFICA'
    AVVIO = 'AVVIO'
    ADOZIONE = 'ADOZIONE'
    APPROVAZIONE = 'APPROVAZIONE'
    PUBBLICAZIONE = 'PUBBLICAZIONE'

    def getNext(self):
        return _FASE_NEXT[self]


_FASE_NEXT = {
    Fase.UNKNOWN: None,
    Fase.DRAFT: Fase.ANAGRAFICA,
    Fase.ANAGRAFICA: Fase.AVVIO,
    Fase.AVVIO: Fase.ADOZIONE,
    Fase.ADOZIONE: Fase.APPROVAZIONE,
    Fase.APPROVAZIONE: Fase.PUBBLICAZIONE,
    Fase.PUBBLICAZIONE: None
}


class TipoRisorsa(SerapideEnum):
    # piano
    DELIBERA = 'delibera'

    # VAS
    RELAZIONE_MOTIVATA = 'relazione_motivata'
    DOCUMENTO_PRELIMINARE_VERIFICA_VAS = 'documento_preliminare_verifica_vas'
    PARERE_VERIFICA_VAS = 'parere_verifica_vas'
    PARERE_SCA = 'parere_sca'
    PARERE_AC = 'parere_ac'
    PROVVEDIMENTO_VERIFICA_VAS = 'provvedimento_verifica_vas'
    DOCUMENTO_PRELIMINARE_VAS = 'documento_preliminare_vas'
    # DOCUMENTO_PRELIMINARE_VAS_SEMPLIFICATO = 'doc_proc_semplificato'
    SINTESI_NON_TECNICA = "sintesi_non_tecnica"

    # avvio
    OBIETTIVI_PIANO = 'obiettivi_piano'
    QUADRO_CONOSCITIVO = 'quadro_conoscitivo'
    PROGRAMMA_ATTIVITA = 'programma_attivita'
    INDIVIDUAZIONE_GARANTE_INFORMAZIONE = 'individuazione_garante_informazione'
    CONTRIBUTI_TECNICI = 'contributi_tecnici'
    ELABORATI_CONFERENZA = 'elaborati_conferenza'
    INTEGRAZIONI = 'integrazioni'
    NORME_TECNICHE_ATTUAZIONE = 'norme_tecniche_attuazione'
    DOCUMENTO_GENIO_CIVILE = 'documento_genio_civile'

    # adozione
    PARERE_ADOZIONE_SCA = 'parere_adozione_sca'
    DELIBERA_ADOZIONE = 'delibera_adozione'
    # adozione - elaborati testuali
    RELAZIONE_GENERALE = "realzaione_generale"
    DISCIPLINA_PIANO = "disciplina_piano"
    RELAZIONE_RESPONSABILE = "relazione_responsabile"
    RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE = "relazione_garante_informazione_partecipazione"
    VALUTAZIONE = "valutazioni"
    ELABORATI_CONFORMAZIONE = "elaborati_conformazione"
    PIANI_ATTUATIVI_BP = "piani_attuativi_beni_paseaggistici"
    INDAGINI_G_I_S = "indagini_geologiche_idrauliche_sismiche"
    # adozione - elaborati cartografici
    SUPPORTO_PREVISIONI_P_C = 'supporto_previsioni_piano_carto'
    DISCIPLINA_INSEDIAMENTI = 'disciplina_insediamenti_esistenti_carto'
    ASSETTI_INSEDIATIVI = 'assetti_insiedativi_infrastrutturali_edilizi_carto'

    OSSERVAZIONI_PRIVATI = 'osservazioni_privati'
    OSSERVAZIONI_ENTI = 'osservazioni_enti'

    ELABORATI_CONF_P = 'elaborati_conferenza_paesaggistica'
    PARERE_MOTIVATO = 'parere_motivato'
    DOCUMENTO_SINTESI = "documento_sintesi"
    RAPPORTO_AMBIENTALE = "rapporto_ambientale"

    # approvazione
    DELIBERA_APPROVAZIONE = "delibera_approvazione"
    CONFORMITA_PIT = "conformita-pit"


TIPOLOGIA_RISORSA = {
    TipoRisorsa.DELIBERA.value: {
        'label': 'Delibera di avvio ',
        'tooltip': 'ai sensi dell’articolo. 17 L.R. 65/2014'
    },
    TipoRisorsa.OBIETTIVI_PIANO.value: {
        'label': 'Obiettivi del Piano',
        'tooltip': ''
    },
    TipoRisorsa.QUADRO_CONOSCITIVO.value: {
        'label': 'Quadro Conoscitivo',
        'tooltip': 'art. 17, lett.b, L.R. 65/2014'
    },
    TipoRisorsa.PROGRAMMA_ATTIVITA.value: {
        'label': 'Programma delle attività di inforamazione ai cittadini',
        'tooltip': ''
    },
    TipoRisorsa.INDIVIDUAZIONE_GARANTE_INFORMAZIONE.value: {
        'label': 'Individuazione del garante dell\'informazione',
        'tooltip': ''
    },

    TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS.value: {
        'label': 'Documento preliminare di verifica assoggettabilità',
        'tooltip': 'art. 22 L.R. 10/2010'
    },
    TipoRisorsa.RELAZIONE_MOTIVATA.value: {
        'label': 'Relazione motivata per verifica VAS semplificata',
        'tooltip': 'art. 5 co.3ter L.R. 10/2010'
    },
    TipoRisorsa.DOCUMENTO_PRELIMINARE_VAS.value: {
        'label': 'Documento preliminare VAS',
        'tooltip': 'art. 23 L.R. 10/2010'
    },
    TipoRisorsa.PARERE_VERIFICA_VAS.value: {
        'label': 'Parere per la verifica VAS',
        'tooltip': ''
    },
    TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS.value: {
        'label': 'Provvedimento di verifica VAS',
        'tooltip': ''
    }
}


class TipologiaPiano(SerapideEnum):
    UNKNOWN = 'UNKNOWN'
    OPERATIVO = 'OPERATIVO'
    STRUTTURALE = 'STRUTTURALE'
    VARIANTE_OPERATIVO = 'Variante operativo'
    VARIANTE_STRUTTURALE = 'Variante strutturale'


class TipologiaVAS(SerapideEnum):
    UNKNOWN = 'UNKNOWN'
    VERIFICA_SEMPLIFICATA = 'Verifica semplificata'
    VERIFICA = 'Verifica'
    PROCEDURA_ORDINARIA = 'Procedura ordinaria'
    PROCEDIMENTO_SEMPLIFICATO = 'Procedimento semplificato'
    NON_NECESSARIA = 'VAS non necessaria'


class TipologiaCopianificazione(SerapideEnum):
    POSTICIPATA = 'Posticipata'
    NECESSARIA = 'Necessaria'
    NON_NECESSARIA = 'Non necessaria'


STATO_AZIONE = Choices(
        ('unknown', _('UNKNOWN')),
        ('nessuna', _('NESSUNA')),
        ('attesa', _('ATTESA')),
        ('necessaria', _('NECESSARIA')),
    )


class TipologiaAzione(SerapideEnum):
    unknown = 'UNKNOWN'
    creato_piano = 'Creato Piano/Variante'  # Comune
    # Procedura VAS
    selezione_tipologia_vas = 'Selezione tipologia VAS'  # OPCOM
    pareri_verifica_sca = 'Pareri verifica VAS'  # SCA
    emissione_provvedimento_verifica = 'Emissione Provvedimento di verifica'  # AC
    pubblicazione_provvedimento_verifica_ac = 'Pubblicazione provvedimento di verifica AC'
    pubblicazione_provvedimento_verifica_ap = 'Pubblicazione provvedimento di verifica AP'
    # avvio_consultazioni_sca = 'Avvio consultazioni SCA'  # Comune/AC
    # pareri_sca = 'Pareri SCA'  # SCA
    # avvio_esame_pareri_sca = 'Avvio esame pareri SCA'  # Comune
    # upload_elaborati_vas = 'Upload elaborati VAS'  # Comune
    invio_doc_preliminare = 'Invio documentazione preliminare'  # Comune
    trasmissione_pareri_sca = 'Trasmissione pareri SCA'  # SCA
    trasmissione_pareri_ac = 'Trasmissione pareri AC'  # AC
    redazione_documenti_vas = 'Redazione documenti VAS'  # Comune
    trasmissione_dpv_vas = 'Trasmissione documento preliminare di verifica'  # AC
    # Avvio
    avvio_procedimento = 'Avvio del Procedimento'  # Comune
    contributi_tecnici = 'Contributi Tecnici'  # Regione
    richiesta_integrazioni = 'Richiesta Integrazioni'  # Regione
    integrazioni_richieste = 'Integrazioni Richieste'  # Comune
    formazione_del_piano = 'Formazione del Piano'  # Comune
    protocollo_genio_civile = 'Protocollo Genio Civile'  # Genio Civile
    richiesta_conferenza_copianificazione = 'Richiesta Conferenza di copianificazione'  # Comune
    esito_conferenza_copianificazione = 'Esito conferenza di copianificazione'  # Regione
    # Adozione
    trasmissione_adozione = 'Trasmissione Adozione'  # Comune
    pubblicazione_burt = 'Pubblicazione BURT'  # Comune
    osservazioni_enti = 'Osservazioni Enti'  # Enti
    osservazioni_regione = 'Osservazioni Regione'  # Regione
    upload_osservazioni_privati = 'Upload Osservazioni Privati'  # Comune
    controdeduzioni = 'Controdeduzioni'  # Comune
    piano_controdedotto = 'Piano Controdedotto'  # Comune
    esito_conferenza_paesaggistica = 'Risultanze conferenza paesaggistica'  # Regione
    rev_piano_post_cp = 'Revisione Piano post Conf. Paesaggistica'  # Comune
    # Adozione VAS
    pareri_adozione_sca = 'Pareri SCA'  # SCA
    parere_motivato_ac = 'Parere Motivato'  # AC
    upload_elaborati_adozione_vas = 'Upload elaborati VAS'  # Comune
    # Approvazione
    trasmissione_approvazione = 'Invio documentazione per Approvazione'  # Comune
    attribuzione_conformita_pit = 'Attribuzione Conformità PIT'  # Regione
    esito_conferenza_paesaggistica_ap = 'Convocazione CP'  # Regione
    pubblicazione_approvazione = 'Pubblicazione Approvazione'  # Comune
    # Pubblicazione
    convocazione_commissione_paritetica = 'Convocazione Commissione Paritetica'  # Comune
    compilazione_finale_monitoraggio_urbanistico = 'Compilazione Finale Monitoraggio Urbanistico'  # Comune
    pubblicazione_piano = 'Pubblicazione Piano'  # Comune


class AzioneInfo:
    def __init__(self, fase: Fase, tooltip=None):
        self.fase = fase
        self.tooltip = tooltip


ART17 = 'art.17 L.R. 65/2014, comma 1, art. 21 Disciplina del Piano , PIT-PPR'
ART19 = 'art.19 L.R. 65/2014'
ART22 = 'art.22 L.R. 10/2010'
ART23 = 'art.23 L.R. 10/2010'
ART25 = 'art.25 L.R. 65/2014'
ART65 = 'art.65/104 RR'

InfoAzioni = {
        TipologiaAzione.unknown: AzioneInfo(Fase.UNKNOWN, 'Unknown'),
        TipologiaAzione.creato_piano: AzioneInfo(Fase.DRAFT),
        # Procedura VAS
        TipologiaAzione.selezione_tipologia_vas: AzioneInfo(Fase.ANAGRAFICA, ART23),
        TipologiaAzione.trasmissione_dpv_vas: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.pareri_verifica_sca: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.emissione_provvedimento_verifica: AzioneInfo(Fase.ANAGRAFICA, ART22),
        TipologiaAzione.pubblicazione_provvedimento_verifica_ac: AzioneInfo(Fase.ANAGRAFICA, ART22),
        TipologiaAzione.pubblicazione_provvedimento_verifica_ap: AzioneInfo(Fase.ANAGRAFICA, ART22),
        # TipologiaAzione.avvio_consultazioni_sca: AzioneInfo(Fase.ANAGRAFICA, ART22),
        # TipologiaAzione.pareri_sca: AzioneInfo(Fase.ANAGRAFICA),
        # TipologiaAzione.avvio_esame_pareri_sca: AzioneInfo(Fase.ANAGRAFICA),
        # TipologiaAzione.upload_elaborati_vas: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.invio_doc_preliminare: AzioneInfo(Fase.ANAGRAFICA, ART22),
        TipologiaAzione.trasmissione_pareri_sca: AzioneInfo(Fase.ANAGRAFICA, ART22),
        TipologiaAzione.trasmissione_pareri_ac: AzioneInfo(Fase.ANAGRAFICA, ART22),
        TipologiaAzione.redazione_documenti_vas: AzioneInfo(Fase.ANAGRAFICA, ART22),
        # Avvio
        TipologiaAzione.avvio_procedimento: AzioneInfo(Fase.ANAGRAFICA, ART17),
        TipologiaAzione.contributi_tecnici: AzioneInfo(Fase.ANAGRAFICA, ART17),
        TipologiaAzione.richiesta_integrazioni: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.integrazioni_richieste: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.formazione_del_piano: AzioneInfo(Fase.ANAGRAFICA),
        TipologiaAzione.protocollo_genio_civile: AzioneInfo(Fase.ANAGRAFICA, ART65),
        TipologiaAzione.richiesta_conferenza_copianificazione: AzioneInfo(Fase.ANAGRAFICA, ART25),
        TipologiaAzione.esito_conferenza_copianificazione: AzioneInfo(Fase.ANAGRAFICA, ART25),
        # Adozione
        TipologiaAzione.trasmissione_adozione: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.pubblicazione_burt: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.osservazioni_enti: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.osservazioni_regione: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.upload_osservazioni_privati: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.controdeduzioni: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.piano_controdedotto: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.esito_conferenza_paesaggistica: AzioneInfo(Fase.AVVIO, ART19),
        TipologiaAzione.rev_piano_post_cp: AzioneInfo(Fase.AVVIO, ART19),
        # Adozione VAS
        TipologiaAzione.pareri_adozione_sca: AzioneInfo(Fase.AVVIO),
        TipologiaAzione.parere_motivato_ac: AzioneInfo(Fase.AVVIO),
        TipologiaAzione.upload_elaborati_adozione_vas: AzioneInfo(Fase.AVVIO),
        # Approvazione
        TipologiaAzione.trasmissione_approvazione: AzioneInfo(Fase.ADOZIONE),
        TipologiaAzione.attribuzione_conformita_pit: AzioneInfo(Fase.ADOZIONE),
        TipologiaAzione.esito_conferenza_paesaggistica_ap: AzioneInfo(Fase.ADOZIONE),
        TipologiaAzione.pubblicazione_approvazione: AzioneInfo(Fase.ADOZIONE),
        # Pubblicazione
        TipologiaAzione.convocazione_commissione_paritetica: AzioneInfo(Fase.APPROVAZIONE),
        TipologiaAzione.compilazione_finale_monitoraggio_urbanistico: AzioneInfo(Fase.APPROVAZIONE),
        TipologiaAzione.pubblicazione_piano: AzioneInfo(Fase.APPROVAZIONE),
}

if len(TipologiaAzione) != len(InfoAzioni):
    raise Exception('Azioni non inizializzate correttamente')


AZIONI_BASE = {
    Fase.DRAFT: [
        {
            "tipologia": TipologiaAzione.creato_piano,
            "qualifica": QualificaRichiesta.COMUNE,
            "stato": STATO_AZIONE.necessaria,
        }
    ],
    Fase.ANAGRAFICA: [
        {
            "tipologia": TipologiaAzione.avvio_procedimento,
            "qualifica": QualificaRichiesta.COMUNE
        }
    ],
    Fase.AVVIO: [
        {
            "tipologia": TipologiaAzione.trasmissione_adozione,
            "qualifica": QualificaRichiesta.COMUNE
        },
    ],
    Fase.ADOZIONE: [
        {
            "tipologia": TipologiaAzione.trasmissione_approvazione,
            "qualifica": QualificaRichiesta.COMUNE
        },
    ],
    Fase.APPROVAZIONE: [
        # {
        #     "tipologia": TIPOLOGIA_AZIONE.convocazione_commissione_paritetica,
        #     "attore": TIPOLOGIA_ATTORE.comune
        # },
        # {
        #     "tipologia": TIPOLOGIA_AZIONE.compilazione_finale_monitoraggio_urbanistico,
        #     "attore": TIPOLOGIA_ATTORE.comune
        # },
        {
            "tipologia": TipologiaAzione.pubblicazione_piano,
            "qualifica": QualificaRichiesta.COMUNE
        },
    ]
}


class TipoExpire(Enum):
    TRASMISSIONE_DPV_VAS = 90
    PARERI_VERIFICA_SCA = 30
    PARERI_VERIFICA_SCA_PROCEDIMENTOSEMPLIFICATO = 30
    EMISSIONE_PV_VERIFICA = 90
    EMISSIONE_PV_VERIFICASEMPLIFICATA = 30
    EMISSIONE_PV_PROCEDIMENTOSEMPLIFICATO = 90

    TRASMISSIONE_PARERI_SCA = 90
    ADOZIONE_VAS_PARERI_SCA_EXPIRE_DAYS = 90


class TipoMail(Enum):
    conferenza_copianificazione = ''
    contributi_tecnici = ''
    esito_conferenza_paesaggistica = ''
    integrazioni_richieste = ''
    message_sent = ''
    parere_motivato_ac = ''
    piano_controdedotto = ''
    piano_phase_changed = ''
    piano_verifica_vas_updated = ''
    protocollo_genio_civile = ''
    pubblicazione_piano = ''
    rev_piano_post_cp = ''
    richiesta_integrazioni = ''
    trasmissione_adozione = ''
    trasmissione_approvazione = ''
    tutti_pareri_inviati = ''
    upload_elaborati_adozione_vas = ''
    azione_generica = ''
