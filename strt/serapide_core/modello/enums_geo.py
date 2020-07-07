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


from serapide_core.modello.enums import (
    TipologiaPiano,
    TipoRisorsa, TipologiaAzione,
)

from strt_users.enums import (
    QualificaRichiesta,
    SerapideEnum)


class PO_CartografiaSupportoPrevisioniEnum(SerapideEnum):
    FEN_GEO_PO = 'Aree ed elementi esposti a fenomeni geologici'
    FEN_ALL_PO = 'Aree ed elementi esposti a fenomeni alluvionali'
    R_SISM_PO = 'Vulnerabilità sismica, esposizione sismica e aree a rischio sismico'
    STRAT_PO = 'Edifici ed infrastrutture strategiche ai fini dell’emergenza'
    RILEV_PO = 'Edifici rilevanti'
    S_PEE_PO = 'Patrimonio Edilizio Esistente e relativa schedatura'


class PO_CartografiaDisciplinaInsediamentiEnum(SerapideEnum):
    CEN_PO = 'Centri o manufatti di valore storico, architettonico o testimoniale'
    NUC_PO = 'Nuclei storici o manufatti di valore storico, architettonico o testimoniale'
    EDI_VAL_PO = 'Edifici o manufatti di valore storico, architettonico o testimoniale'
    I_PEE_PO = 'Interventi sul patrimonio edilizio esistente realizzabili nel territorio urbanizzato'
    ARU_PO = 'Aree Rurali'
    NUR_PO = 'Nuclei rurali'
    NAT_PO = 'Aree ad elevato grado di naturalità'
    AUF_PO = 'Ulteriori aree'
    APT_PO = 'Ambiti di pertinenza dei centri e dei nuclei storici'
    APU_PO = 'Ambiti periurbani'
    PAI_PO = 'Paesaggi agrari e pastorali di interesse storico'
    ATD_PO = 'Ambiti territoriali differenziati del Territorio Rurale'
    DL_FUN = 'Distribuzione e localizzazione delle funzioni'
    POR_PO = 'Ambiti portuali del territorio comunale, entro i quali le previsioni si attuano tramite il piano regolatore portuale'
    DEG_PO = 'Zone connotate da condizioni di degrado'


class PO_CartografiaAssettiInsediativiEnum(SerapideEnum):
    PAT_PO = 'Aree interessate da piani attuativi'
    RIG_PO = 'Aree interessate da interventi di rigenerazione urbana'
    PUC_PO = 'Aree interessate da progetti unitari convenzionati'
    NED_PO = 'Ulteriori aree interessate da nuova edificazione consentiti all’interno del perimetro del territorio urbanizzato'
    INT_COP_PO = 'Nuovi impegni di suolo esterni al perimetro del territorio urbanizzato copianificati'
    OUP_PO = 'Aree destinate ad opere di urbanizzazione primaria'
    OUS_PO = 'Aree destinate ad opere di urbanizzazione secondaria'
    ESP_PO = 'Beni sottoposti a vincolo ai fini espropriativi'
    PCP_PO = 'Aree interessate da perequazione urbanistica, la compensazione urbanistica, perequazione territoriale'
    E_INC = 'Edifici esistenti non più compatibili con gli indirizzi della pianificazione'


class PS_QuadroConoscitivoEnum(SerapideEnum):
    FFO_PS = 'Frequenze fondamentali'
    IDR_PS = 'Idrogeologia'
    P_GEO_PS = 'Pericolosità geologica'
    P_SIL_PS = 'Pericolosità sismica locale'
    P_ALL_PS = 'Pericolosità da alluvioni'
    B_ALL_PS = 'Battente'
    V_ALL_PS = 'Velocità della corrente'
    MAG_PS = 'Magnitudo idraulica'
    ARG_PS = 'Aree presidiate da sistemi arginali'
    FVF_PS = 'Aree di fondovalle fluviale'
    QC_TU_PS = 'Quadro conoscitivo a supporto dell’individuazione del perimetro del Territorio Urbanizzato'


class PS_StatutoDelTerritorioEnum(SerapideEnum):
    PAT_ECO_PS = 'Struttura ecosistemica del Patrimonio Territoriale comunale'
    PAT_INS_PS = 'Struttura insediativa del Patrimonio Territoriale comunale'
    PAT_AGF_PS = 'Struttura agro-forestale del Patrimonio Territoriale comunale'
    PAT_PERC_PS = 'Elementi di carattere percettivo'
    MOD_142 = 'Aree tutelate per legge - modifiche'
    APA_CI = 'Aree di potenziale tutela attenuata dei corpi idrici'
    AGCD = 'Aree gravemente compromesse o degradate'
    RIN_CI = 'Corpi idrici rinvenuti ai sensi del punto 4.4 dell’elaborato 7B,'
    DE_CI = 'Derubricazione di corpi idrici'
    RCBP_IDROGEO = 'Riconoscimenti riferiti alla Struttura idrogeomorfologica'
    RCBP_ECOAMB = 'Riconoscimenti riferiti alla Struttura ecosistemica/ambientale'
    RCBP_ANTR = 'Riconoscimenti riferiti alla Struttura antropica'
    RCBP_PERC = 'Riconoscimenti riferiti agli Elementi della percezione'
    RCBP_a = 'Riconoscimenti relativi ai Territori costieri'
    RCBP_b = 'Riconoscimenti relativi ai Territori contermini ai laghi'
    RCBP_c = 'Riconoscimenti relativi ai fiumi, i torrenti, i corsi d''acqua'
    RCBP_g = 'Riconoscimenti relativi ai territori coperti da foreste e da boschi'
    RCBP_h = 'Riconoscimenti relativi alle zone gravate da usi civici'
    RCBP_m = 'Riconoscimenti relativi alle zone di interesse archeologico'
    I_INV_PS = 'I Invariante Strutturale - caratteri idro-geo-morfologici dei bacini idrografici e dei sistemi morfogenetici'
    II_INV_STR_PS = 'II Invariante Strutturale - caratteri ecosistemici dei paesaggi (STR)'
    II_INV_FUN_PS = 'II Invariante Strutturale - caratteri ecosistemici dei paesaggi (FUN)'
    III_INV_PS = 'III Invariante Strutturale - carattere policentrico e reticolare dei sistemi insediativi, urbani e infrastrutturali'
    IV_INV_PS = 'IV Invariante Strutturale - caratteri morfotipologici dei sistemi agro ambientali dei paesaggi rurali'
    TU_PS = 'Perimetro del territorio urbanizzato'
    CEN_PS = 'Centri storici'
    NUC_PS = 'Nuclei storici'
    APT_PS = 'Ambiti di pertinenza dei centri e dei nuclei storici'
    CFLU_PS = 'Contesti fluviali (art.'


class PS_StrategiaEnum(SerapideEnum):
    UTOE_PS = 'Unità Territoriali Organiche Elementari'
    A_TLI_PS = 'Ambiti territoriali di localizzazione interventi'
    INT_COP_PS = 'Nuovi impegni di suolo esterni al perimetro del territorio urbanizzato copianificati'
    A_DEG_PS = 'Ambiti caratterizzati da condizioni di degrado'
    PER_ACC = 'Percorsi accessibili per la fruizione delle funzioni pubbliche urbane'
    COR_INFRA_PS = 'Ambiti di realizzazione, potenziamento, salvaguardia delle infrastrutture stradali e ferroviarie'


MAPPING_PIANO_RISORSE = {
    TipologiaPiano.OPERATIVO: (
        TipoRisorsa.ASSETTI_INSEDIATIVI,
        TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
        TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
    ),
    TipologiaPiano.STRUTTURALE: (
        TipoRisorsa.DELIBERA,  # TODO
        TipoRisorsa.DELIBERA,  # TODO
        TipoRisorsa.DELIBERA,  # TODO
    ),
    # TipologiaPiano.VARIANTE_OPERATIVO: (
    # ),
    # TipologiaPiano.VARIANTE_STRUTTURALE: (
    # ),
}


MAPPING_RISORSA_ENUM = {
    TipoRisorsa.ASSETTI_INSEDIATIVI: PO_CartografiaAssettiInsediativiEnum,
    TipoRisorsa.DISCIPLINA_INSEDIAMENTI: PO_CartografiaDisciplinaInsediamentiEnum,
    TipoRisorsa.SUPPORTO_PREVISIONI_P_C: PO_CartografiaSupportoPrevisioniEnum,

    TipoRisorsa.DELIBERA: PS_StrategiaEnum,  # TODO
    TipoRisorsa.DELIBERA: PS_QuadroConoscitivoEnum,  # TODO
    TipoRisorsa.DELIBERA: PS_StatutoDelTerritorioEnum,  # TODO
}

MAPPING_AZIONI_CARTO_NEXT = {
    TipologiaAzione.trasmissione_adozione:
        TipologiaAzione.validazione_cartografia_adozione,
    TipologiaAzione.piano_controdedotto:
        TipologiaAzione.validazione_cartografia_controdedotta,
    TipologiaAzione.rev_piano_post_cp:
        TipologiaAzione.validazione_cartografia_cp_adozione,
    TipologiaAzione.trasmissione_approvazione:
        TipologiaAzione.validazione_cartografia_approvazione,
    TipologiaAzione.esito_conferenza_paesaggistica_ap:
        TipologiaAzione.validazione_cartografia_cp_approvazione
}