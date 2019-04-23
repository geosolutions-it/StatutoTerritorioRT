/**
 * Elaborati testuali e cartografici per tipo di piano
 */

const testuali = { "realzaione_generale": {label: "RELAZIONE GENERALE", tooltip: "art. 4 comma 2 Regolamento 4/R/2017 e art. 95 comma 5 l.r. 65/2014"},
"disciplina_piano": {label: "DISCIPLINA DEL PIANO", tooltip: "art. 95 della l.r. 65/2014"},
"relazione_responsabile": {label: "RELAZIONE TECNICA RESPONSABILE DEL PROCEDIMENTO", tooltip: "art. 95 comma 7 l.r. 65/2014"},
"relazione_garante_informazione_partecipazione" : {label: "RELAZIONE DEL GARANTE DELL’INFORMAZIONE E DELLA PARTECIPAZIONE", tooltip: "art. 38 comma 2 l.r. 65/2014"},
"valutazioni": {label: "VALUTAZIONI", tooltip: "art. 14 l.r. 65/2014; l.r. 10/2010"},
"elaborati_conformazione": {label: "ELABORATI DI ADEGAUMENTO CONFORMAZIONE", tooltip: "art. 3 comma 4 Accordo MIBACT-Regione Toscana del 16.12.2016"}
}

const cartografici =  {
    "supporto_previsioni_piano_carto": {label: "ELABORATI CARTOGRAFICI DI SUPPORTO ALLE PREVISIONI DEL PIANO", tooltip:"ai sensi art. 95 comma 5 della l.r. 65/2014"},
    "disciplina_insediamenti_esistenti_carto": {label:"ELABORATI CARTOGRAFICI INERENTI LA DISCIPLINA PER LA GESTIONE DEGLI INSEDIAMENTI ESISTENTI", tooltip: "ai sensi art. 95 comma 2 della l.r. 65/2014"},
    "assetti_insiedativi_infrastrutturali_edilizi_carto": {label:"ELABORATI CARTOGRAFICI INERENTI LE TRASFORMAZIONI DEGLI ASSETTI INSEDIATIVI, INFRASTRUTTURALI ED EDILIZI", tooltip: "ai sensi art. 95 comma 3 della l.r. 65/2014"},
}

export default {
    "operativo": {
        "testuali":{
            ...testuali,
            "piani_attuativi_beni_paseaggistici": {label: "SCHEDE NORMA PIANI ATTUATIVI BENI PAESAGGISTICI", tooltip: "art. 4 comma 5 Accordo MIBACT-Regione Toscana del 16.12.2016"},
            "indagini_geologiche_idrauliche_sismiche": {label: "RELAZIONE INDAGINI GEOLOGICHE-IDRAULICHE-SISMICHE", tooltip: "art.104 comma 9 l.r. 65/2014"}
        },
        cartografici
    },
    "strutturale": {
        testuali,
        cartografici
    },
    "variante_operativo": {
        "testuali":{
            ...testuali,
            "piani_attuativi_beni_paseaggistici": {label: "SCHEDE NORMA PIANI ATTUATIVI BENI PAESAGGISTICI", tooltip: "art. 4 comma 5 Accordo MIBACT-Regione Toscana del 16.12.2016"},
            "indagini_geologiche_idrauliche_sismiche": {label: "RELAZIONE INDAGINI GEOLOGICHE-IDRAULICHE-SISMICHE", tooltip: "art.104 comma 9 l.r. 65/2014"}
        },
        cartografici
    },
    "variante_strutturale": {
        testuali,
        cartografici
    }
}