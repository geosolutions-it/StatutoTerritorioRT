/*
 * Copyright 2018, GeoSolutions Sas.
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
        "AVVIO_PROCEDIMENTO": ["RUP", "OP"],
        "PARERI_VERIFICA_VAS" : ["TMP", ""],
        "RICHIESTA_VERIFICA_VAS": ["", ""],
        "PARERI_VERIFICA_SCA": ["TMP"],
        "EMISSIONE_PROVVEDIMENTO_VERIFICA": ["TMP"],
        "PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA": ["TMP", "RUP", "OP"],
        "AVVIO_CONSULTAZIONI_SCA": ["RUP", "OP", "TMP"],
        "PARERI_SCA": ["TMP"],
        "AVVIO_ESAME_PARERI_SCA": ["RUP", "OP"],
        "UPLOAD_ELABORATI_VAS": ["RUP", "OP"],
        "FORMAZIONE_DEL_PIANO": ["RUP", "OP"],
        "PROTOCOLLO_GENIO_CIVILE_ID": ["GENIO_CIVILE"]
    }
export const globalAuth = {
    _attore_attivo: "",
    _ruolo: ""
}


export const checkAttore = ( {attore = ""} = {}, attore_attivo = globalAuth._attore_attivo) => attore === attore_attivo

export const canExecuteAction = ({tipologia = "", attore= ""} = {}, attore_attivo = globalAuth._attore_attivo, ruolo = globalAuth._ruolo) => {
 // console.log(attore_attivo, ruolo, tipologia, attore, includes((azioni[tipologia] || []), ruolo) );
  return attore_attivo.toLowerCase() === attore.toLowerCase() && includes((azioni[tipologia] || []), ruolo) 
}