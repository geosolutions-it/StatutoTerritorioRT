/**
 * Elaborati testuali e cartografici per tipo di piano
 */

const testuali_comuni = {
    "realzaione_generale": {order: 0, label: "RELAZIONE GENERALE", tooltip: "art. 4 comma 2 Regolamento 4/R/2017 e art. 95 comma 5 l.r. 65/2014"},
    "disciplina_piano": {order: 1, label: "DISCIPLINA DEL PIANO", tooltip: "art. 95 della l.r. 65/2014"},
    "indagini_geologiche_idrauliche_sismiche": {order: 4, label: "RELAZIONE INDAGINI GEOLOGICHE IDRAULICHE SISMICHE", tooltip: "art.104 comma 9 l.r. 65/2014"},
    "relazione_responsabile": {order: 5, label: "RELAZIONE TECNICA RESPONSABILE DEL PROCEDIMENTO", tooltip: "art. 95 comma 7 l.r. 65/2014"},
    "relazione_garante_informazione_partecipazione" : {order: 6, label: "RELAZIONE DEL GARANTE DELL’INFORMAZIONE E DELLA PARTECIPAZIONE", tooltip: "art. 38 comma 2 l.r. 65/2014"},
    "valutazioni": {order: 7, label: "VALUTAZIONI", tooltip: "art. 14 l.r. 65/2014; l.r. 10/2010", fileType: "application/zip,application/x-zip-compressed,.zip", icon: "archive"},

}

const testuali_operativo = {
    "piani_attuativi_beni_paseaggistici": {order: 2, label: "SCHEDE NORMA PIANI ATTUATIVI BENI PAESAGGISTICI", tooltip: "art. 4 comma 5 Accordo MIBACT-Regione Toscana del 16.12.2016"},
    "elaborati_adeguamento_conformazione": {order: 8, label: "ELABORATI DI ADEGUAMENTO CONFORMAZIONE", tooltip: "art. 3 comma 4 Accordo MIBACT-Regione Toscana del 16.12.2016"}
}

const testuali_strutturale = {
    
    "elaborati_conformazione": {order: 8, label: "ELABORATI DI CONFORMAZIONE", tooltip: "art. 3 comma 4 Accordo MIBACT-Regione Toscana del 16.12.2016"}
    
}
const cartografici =  {
    "supporto_previsioni_piano_carto": {order:0, label: "ELABORATI CARTOGRAFICI DI SUPPORTO ALLE PREVISIONI DEL PIANO", tooltip:"ai sensi art. 95 comma 5 della l.r. 65/2014"},
    "disciplina_insediamenti_esistenti_carto": {order:1, label:"ELABORATI CARTOGRAFICI INERENTI LA DISCIPLINA PER LA GESTIONE DEGLI INSEDIAMENTI ESISTENTI", tooltip: "ai sensi art. 95 comma 2 della l.r. 65/2014"},
    "assetti_insiedativi_infrastrutturali_edilizi_carto": {order:2, label:"ELABORATI CARTOGRAFICI INERENTI LE TRASFORMAZIONI DEGLI ASSETTI INSEDIATIVI, INFRASTRUTTURALI ED EDILIZI", tooltip: "ai sensi art. 95 comma 3 della l.r. 65/2014"},
}

export default {
    "operativo": {
        "testuali":{
            ...testuali_comuni ,
            ...testuali_operativo
        },
        cartografici
    },
    "strutturale": {
        "testuali" : {
            ...testuali_comuni,
            ...testuali_strutturale
        } ,
        cartografici
    },
    "variante_operativo": {
        "testuali":{
            ...testuali_comuni ,
            ...testuali_operativo
        },
        cartografici
    },
    "variante_strutturale": {
        "testuali" : {
            ...testuali_comuni,
            ...testuali_strutturale
        },
        cartografici
    }
}