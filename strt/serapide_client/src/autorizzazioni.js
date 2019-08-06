/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import {includes} from "lodash"

 /**
  * Implementa la logica per autorizzare le azioni
  * Come tipi al momento attuale come da modello django-admin/strt_users/membershiptype/ TMP RO RI OP IPT IVAS RUP
  * detti ruoli possono appartenere ad attori differenti
  * Attori da enums: Comune Regione AC SCA Genio Civile
  *
  */
const azioni = {
        "AVVIO_PROCEDIMENTO": ["RUP", "TMP", "OP"],
        "PARERI_VERIFICA_VAS" : ["TMP", "OP", "RUP"],
        "RICHIESTA_VERIFICA_VAS": ["", "RUP"],
        "PARERI_VERIFICA_SCA": ["TMP", "OP","RUP"],
        "EMISSIONE_PROVVEDIMENTO_VERIFICA": ["TMP", "OP", "RUP"],
        "PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA": ["TMP", "RUP", "OP"],
        "AVVIO_CONSULTAZIONI_SCA": ["RUP", "OP", "TMP"],
        "PARERI_SCA": ["TMP", "OP", "RUP"],
        "AVVIO_ESAME_PARERI_SCA": ["RUP", "TMP", "OP", "RUP"],
        "UPLOAD_ELABORATI_VAS": ["RUP", "TMP", "OP"],
        "FORMAZIONE_DEL_PIANO": ["RUP", "TMP", "OP"],
        "PROTOCOLLO_GENIO_CIVILE_ID": ["*"],
        "RICHIESTA_CONFERENZA_COPIANIFICAZIONE": ["RUP", "OP"],
        "CONVOCAZIONE_CONFERENZA_COPIANIFICAZIONE": ["RUP","TMP", "OP"],
        "ESITO_CONFERENZA_COPIANIFICAZIONE": ["TMP", "OP", "RUP"],
        "RICHIESTA_INTEGRAZIONI": ["TMP", "OP", "RUP"],
        "INTEGRAZIONI_RICHIESTE": ["RUP", "TMP", "OP"],
        "TRASMISSIONE_ADOZIONE": ["RUP", "TMP", "OP"],
        "UPLOAD_OSSERVAZIONI_PRIVATI": ["RUP", "TMP", "OP"],
        "OSSERVAZIONI_ENTI": ["*"],
        "OSSERVAZIONI_REGIONE": ["TMP", "OP","RUP"],
        "CONTRODEDUZIONI": ["RUP", "OP", "TMP"],
        "PIANO_CONTRODEDOTTO": ["RUP", "OP", "TMP"],
        "ESITO_CONFERENZA_PAESAGGISTICA": ["RUP", "OP", "TMP"],
        "REV_PIANO_POST_CP": ["RUP", "OP", "TMP"],
        "PARERI_ADOZIONE_SCA": ["TMP", "OP","RUP"],
        "PARERE_MOTIVATO_AC": ["TMP", "OP","RUP"],
        "UPLOAD_ELABORATI_ADOZIONE_VAS": ["RUP", "OP", "TMP"],
        "TRASMISSIONE_APPROVAZIONE": ["RUP", "OP", "TMP"],
        "ESITO_CONFERENZA_PAESAGGISTICA_AP": ["RUP", "OP", "TMP"],
        "REV_PIANO_POST_CP_AP": ["RUP", "OP", "TMP"],
        "ATTRIBUZIONE_CONFORMITA_PIT": ["RUP", "OP", "TMP"],
        "PUBBLICAZIONE_APPROVAZIONE": ["RUP", "OP", "TMP"],
        "PUBBLICAZIONE_PIANO": ["RUP", "OP", "TMP"],
        "CONTRIBUTI_TECNICI": ["*"]
    }
export const globalAuth = {
    _attore_attivo: "",
    _ruolo: ""
}
// Attenzione OSSERVAZIONI ENTI PASSA DIRETTAMENTE NON HA CONTROLLO

export const checkAttore = ( {attore = ""} = {}, attore_attivo = globalAuth._attore_attivo) => attore === attore_attivo

export const canExecuteAction = ({tipologia = "", attore= ""} = {}, attore_attivo = globalAuth._attore_attivo, ruolo = globalAuth._ruolo) => {
  // console.log(attore_attivo, ruolo, tipologia, attore, includes((azioni[tipologia] || []), ruolo) );
  return tipologia === "OSSERVAZIONI_ENTI" || (attore_attivo.toLowerCase() === attore.toLowerCase() && (includes((azioni[tipologia] || []), ruolo) || includes((azioni[tipologia] || []), "*")))
}
