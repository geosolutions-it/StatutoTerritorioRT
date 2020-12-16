/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import snakeCase from 'lodash/snakeCase';
import wms from '@mapstore/observables/wms';

import invarianti from '../static/mapstore/layers/invarianti.json';
import pianiOperativi from '../static/mapstore/layers/piani_operativi.json';
import pianiStrutturali from '../static/mapstore/layers/piani_strutturali.json';
import pianoPaesaggisticoRegionale from '../static/mapstore/layers/piano_paesaggistico_regionale.json';

const bgLayers = [{
    "id": "mapnik__0",
    "group": "background",
    "source": "osm",
    "name": "mapnik",
    "title": "Open Street Map",
    "type": "osm",
    "visibility": true,
    "singleTile": false,
    "dimensions": [],
    "hideLoading": false,
    "handleClickOnLayer": false,
    "useForElevation": false,
    "hidden": false
},
{
    "id": "Night2012__3",
    "group": "background",
    "source": "nasagibs",
    "name": "Night2012",
    "provider": "NASAGIBS.ViirsEarthAtNight2012",
    "title": "NASAGIBS Night 2012",
    "type": "tileprovider",
    "visibility": false,
    "singleTile": false,
    "dimensions": [],
    "hideLoading": false,
    "handleClickOnLayer": false,
    "useForElevation": false,
    "hidden": false
},
{
    "id": "OpenTopoMap__4",
    "group": "background",
    "source": "OpenTopoMap",
    "name": "OpenTopoMap",
    "provider": "OpenTopoMap",
    "title": "OpenTopoMap",
    "type": "tileprovider",
    "visibility": false,
    "singleTile": false,
    "dimensions": [],
    "hideLoading": false,
    "handleClickOnLayer": false,
    "useForElevation": false,
    "hidden": false
},
{
    "id": "undefined__5",
    "group": "background",
    "source": "ol",
    "title": "Empty Background",
    "type": "empty",
    "visibility": false,
    "singleTile": false,
    "dimensions": [],
    "hideLoading": false,
    "handleClickOnLayer": false,
    "useForElevation": false,
    "hidden": false
}];

const mappaBase = (layers, groups) => ({
    "version": "2",
    "map": {
        "center": {
            "crs": "EPSG:4326",
            "x": 10.507665429687545,
            "y": 43.26966280764068
        },
        "maxExtent": [
            -20037508.34,
            -20037508.34,
            20037508.34,
            20037508.34
        ],
        "projection": "EPSG:900913",
        "units": "m",
        "zoom": 8,
        "info": {
            "canEdit": false
        },
        layers: [
            ...bgLayers,
            ...layers
        ],
        groups
    }
});

/*
// snippet to get info in the html page
let arr = []
let nodes = [...document.querySelectorAll('dl')]

for (let i = 0; i < nodes.length; i++) {
    arr.push([
        nodes[i].querySelector('table > tbody > tr > td > b').innerText,
        nodes[i].querySelector('table > tbody > tr > td > table > tbody > tr > td').innerText
    ])
}

console.log(JSON.stringify(arr));
*/

const pianoPaesaggisticoRegionaleArray = [
    [
        "rt_piapae.idambpae.rt.poly",
        "Ambiti di Paesaggio",
        "Gli Ambiti di paesaggio descrivono i caratteri peculiari e le caratteristiche paesaggistiche del territorio regionale derivanti dalla natura, dalla storia e dalle loro interrelazioni e, in riferimento ai quali, il Piano definisce specifici obiettivi di qualita' e normative d'uso. Il territorio di ciascun Ambito e' composto da un insieme di comuni, eccetto il caso del comune di Castelnuovo Berardenga, il cui territorio e' ripartito fra due Ambiti distinti. Dataset areale: 'Ambiti di paesaggio'. Scala di visibilita 1:1 - 1:5.000.000. Territorio coperto: intera regione."
    ],
    [
        "lett_a_artut",
        "Aree tutelate per legge - Lettera a) - I territori costieri",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Buffer realizzato a partire dalla linea di costa individuata con foto restituzione stereoscopica alla scala 1:10.000 da fotogrammi aerei del 2010. Dataset areale, 'Aree tutelate - I Sistemi costieri'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intera fascia costiera regionale."
    ],
    [
        "lett_b_laghi",
        "Aree tutelate per legge - Lettera b) - I territori contermini ai laghi",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Buffer realizzato a partire dalla linea di riva degli specchi d'acqua con perimetro maggiore o uguale a 500 ml, presenti nel Sistema acque_CTR 10K della Regione Toscana. Dataset areale: 'Aree tutelate - I Sistemi costieri'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "specchi_acqua500m",
        "Specchi d'acqua 500 metri",
        "Specchi d'acqua con perimetro maggiore di 500 ml, presenti nel Sistema acque_CTR 10K della Regione Toscana. Dataset areale: 'Specchi d'acqua con perimetro maggiore di 500 ml'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_c_aree_tutelate",
        "Aree tutelate per legge - Lettera c) - I fiumi, i torrenti, i corsi d'acqua",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Buffer realizzato a partire da grafo idrico (mezzeria del corso d'acqua) ovvero, quando possibile, dalla linea di identificazione dell'area bagnata o dell'area idrica dei corsi d'acqua presenti nel Sistema acque /CTR 10K della Regione Toscana. Dataset areale: 'Aree tutelate'.Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_c_fiumi",
        "Fiumi, torrenti, corsi d'acqua",
        "Grafo dei soli corsi d'acqua interessati, in tutto o in parte, da aree di tutela, presenti nel Sistema acque _CTR 10K della Regione Toscana."
    ],
    [
        "rt_piapae.grafo.sistema.acque.rt",
        "Grafo Sistema acque_CTR",
        "Grafo del Sistema acque _CTR 10K della Regione Toscana. Lo strato e' una riproposizione di quello dei corsi d'acqua presente nel WMS 'IDROGRAFIA'.Dataset lineare: 'Grafo Sistema acque_CTR'. Scala di visibilita' 1:1 - 1:5000000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_d_artut",
        "Aree tutelate per legge - Lettera d) - Le montagne per la parte eccedente 1.200 msl",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Aree individuate a partire dalle curve di livello rappresentate nel database topografico della Regione Toscana. Dataset areale: 'Aree tutelate'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_e_artut",
        "Aree tutelate per legge - Lettera e) - I circhi glaciali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Aree individuate con foto restituzione stereoscopica alla scala 1:10.000 da fotogrammi aerei del 2010 e verifica di campo. Dataset areale: 'Aree tutelate'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idparnaz.rt.poly",
        "Aree tutelate per legge - Lett. f) Parchi nazionali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. I confini dei parchi nazionali sono definiti e approvati dagli Enti parco competenti. Lo strato e' una riproposizione di quello dei parchi nazionali presente nel WMS 'Aree protette'. Dataset areale: 'Parchi nazionali'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idrisnatstat.rt.poly",
        "Aree tutelate per legge - Lett. f) - Riserve statali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. I confini delle riserve statali sono definiti e approvati dall' Ente statale competente. Lo strato e' una riproposizione di quello delle riserve statali presente nel WMS 'Aree protette'.Dataset areale: 'Riserve statali'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idparreg.rt.poly",
        "Aree tutelate per legge - Lett. f) - Parchi regionali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. I confini dei parchi regionali sono definiti e approvati dagli Enti parco competenti. Lo strato e' una riproposizione di quello dei parchi regionali presente nel WMS 'Aree protette'. Dataset areale: 'Parchi regionali'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idparprov.rt.poly",
        "Aree tutelate per legge - Lett. f) - Parchi provinciali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. I confini dei parchi provinciali sono definiti e approvati dagli Enti provinciali competenti. Lo strato e' una riproposizione di quello dei parchi provinciali presente nel WMS 'Aree protette'. Dataset areale: 'Parchi provinciali'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idrisnatprov.rt.poly",
        "Aree tutelate per legge - Lett. f) - Riserve naturali provinciali",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. I confini delle riserve naturali provinciali sono definiti e approvati dagli Enti provinciali competenti. Lo strato e' una riproposizione di quello delle riserve naturali provinciali presente nel WMS 'Aree protette'. Dataset areale: 'Riserve provinciali'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_g_artut",
        "Aree tutelate per legge - Lett. g) - I territori coperti da foreste e da boschi - aggiornamento DCR 93/2018",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Il dataset e' composto dalla Classe 1 (Boschi), della Classe 1bis (Strade in aree boscate) e della Classe 2 (Aree assimilabili a bosco) estratte dal database 'Uso e copertura del suolo' della Regione Toscana, foto interpretato da OFC dell'anno 2010 alla scala 1:10.000. Lo strato e' una riproposizione di quello gia' presente nel WMS 'Uso e copertura del suolo'. Dataset areale: 'Aree tutelate'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale. Il dataset e' un aggiornamento con DCR 93/2018."
    ],
    [
        "lett_g_artut_20150327_20181009",
        "Aree tutelate per legge - Lett. g) - I territori coperti da foreste e da boschi - Dato storico",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Il dataset e' composto dalla Classe 1 (Boschi), della Classe 1bis (Strade in aree boscate) e della Classe 2 (Aree assimilabili a bosco) estratte dal database 'Uso e copertura del suolo' della Regione Toscana, foto interpretato da OFC dell'anno 2010 alla scala 1:10.000. Lo strato e' una riproposizione di quello gia' presente nel WMS 'Uso e copertura del suolo'. Dataset areale: 'Aree tutelate'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale. Dato storico. Riferito alla data del 27/03/2015."
    ],
    [
        "lett_h_usicivici",
        "Aree tutelate per legge - Lett. h) - Le zone gravate da usi civici",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Lo strato propone i comuni nei quali vi e' una presenza o assenza accertata di Usi civici nonche' di quelli in cui l'accertamento non e' stato eseguito. Dataset areale: 'Comuni'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_i_artut",
        "Aree tutelate per legge - Lett. i) - Le zone umide",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 142. Lo strato propone i perimetri delle aree individuate ai sensi della convenzione internazionale di Ramsar relativa alle zone umide di importanza internazionale, sottoscritta nel 1971 da un gruppo di paesi, istituzioni scientifiche ed organizzazioni internazionali. Lo strato e' una riproposizione di quello delle zone umide ramsar presente nel WMS 'Aree protette'. Dataset areale: 'Aree tutelate'. Scala di visibilita 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "lett_m_artut",
        "Aree tutelate per legge - Lett. m) - Le zone di interesse archeologico.",
        "Zone tutelate di cui all'art. 11.3 lett. a) e b) dell'Elaborato 7B della Disciplina dei beni paesaggistici. Dataset areale: 'Zone tutelate di cui all'art. 11.3 lett. a) e b) dell'Elaborato 7B della Disciplina dei beni paesaggistici'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.vinc_archeo_ricad",
        "Aree tutelate per legge - Lett. m) - Le zone di interesse archeologico - Beni archeologici tutelati ai sensi della parte II del D.Lgs. 42/2004 con valenza paesaggistica ricadenti nelle zone tutelate di cui all'art. 11.3 lett. a) e b)",
        "Dataset areale: ' Le zone di interesse archeologico - Beni archeologici tutelati ai sensi della parte II del D.Lgs. 42/2004 con valenza paesaggistica ricadenti nelle zone tutelate di cui all'art. 11.3 lett. a) e b)'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale. Avvertenza: l'attestazione dei vincoli culturali viene rilasciata dalla competente Soprintendenza."
    ],
    [
        "rt_piapae.vinc_archeo_coinc_1",
        "Aree tutelate per legge - Lett. m) - Le zone di interesse archeologico - Zone tutelate di cui all'art. 11.3 lett. c) dell'Elaborato 7B della Disciplina dei beni paesaggistici.",
        "Dataset areale: 'Zone tutelate di cui all'art. 11.3 lett. c) dell'Elaborato 7B della Disciplina dei beni paesaggistici'. Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale. Avvertenza: l'attestazione dei vincoli culturali viene rilasciata dalla competente Soprintendenza."
    ],
    [
        "rt_piapae.vinc_archeo_coinc_2",
        "Aree tutelate per legge - Lett. m) - Le zone di interesse archeologico - Beni archeologici tutelati ai sensi della parte II del D.Lgs. 42/2004 con valenza paesaggistica coincidenti con le zone tutelate di cui all'art. 11.3 lett. c)",
        "Dataset areale: 'Le zone di interesse archeologico - Beni archeologici tutelati ai sensi della parte II del D.Lgs. 42/2004 con valenza paesaggistica coincidenti con le zone tutelate di cui all'art. 11.3 lett. c). Scala di visibilita' 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale Avvertenza: l'attestazione dei vincoli culturali viene rilasciata dalla competente Soprintendenza."
    ],
    [
        "ulter_cont_unesco",
        "Ulteriori contesti",
        "Lo strato propone i perimetri delle aree individuate in Toscana dalla Commissione per il Patrimonio Mondiale quali siti con valore universale."
    ],
    [
        "rt_piapae.idpae1_a.rt",
        "Immobili ed aree di notevole interesse pubblico",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 136. Dataset areale: 'Immobili ed aree di notevole interesse pubblico'. Scala di visibilita 1:1 - 1:5.000.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.idpae1_a_etichette.rt",
        "Etichette degli immobili ed aree di notevole interesse pubblico",
        "Aree di tutela individuate ai sensi del D.lgs. 42/2004, art 136. Dataset areale: 'Immobili ed aree di notevole interesse pubblico'. Etichette. Scala di visibilita 1:1 - 1:100.000. Territorio coperto: intero territorio regionale."
    ],
    [
        "rt_piapae.topografica50k.color.rt",
        "Carta topografica 1:50.000",
        "Carta topografica 1:50.000. Lo strato propone la Carta topografica regionale in scala 1:50.000 in versione a colori. La carta e' stata realizzata elaborando le seguenti fonti cartografiche principali: Viabilita': DataBaseTopografico_Regione Toscana_(2000_2010); OpenStreetMap_2012) - Linee ferroviarie: DBT_RT_(2000_2010) - Insediamenti: DBT_RT_(2000_2010); BD_Catastale_AdT_(2012) - Infrastrutture e attrezzature: Fotointerpretazione da OFC_AGEA_RT_(2010) - Uso e Copertura del suolo: UCS_RT_(2007) - Toponomastica: DBT_RT_(2000_2010); IGM - Idrografia e zone umide: DBT_RT_(2000_2010) - Orografia: DBT_RT_(2000_2010); LaRIST - Batimetria: DBT_RT_(2000_2010)."
    ],
    [
        "rt_piapae.carta_dei_caratteri_del_paesaggio.50k.ct.rt",
        "Carta dei caratteri del paesaggio 1:50.000",
        "Carta dei caratteri del paesaggio 1:50.000. Lo strato propone la Carta dei caratteri del paesaggio in scala 1:50.000. La carta e' stata realizzata elaborando le seguenti fonti cartografiche principali: Rilievo ombreggiato: DBT_RT_(2000_2010); LaRIST - Tipi fisiografici: CIST_(2013) - Calanchi e biancane: DB_CARG_RT_(.....); QC_PTCP - Idrografia e zone umide: DBT_RT_(2000_2010) - Fonti Termali: QC_PTCP - Batimetria: DBT_RT_(2000_2010) - Caratteri vegetazionali: UCS_RT_(2007); IFT_RT_(2009); Carta della Vegetazione_ Arrigoni_RT_(1998); Fotointerpretazione da OFC_AGEA_RT_(2010) - Vegetazione Riparia: UCS_RT_(2007); DB_CARG_RT_(2010); QC_PTCP - Alberate: QC_PTC - Allineamento centuriazione: QC_PTC - Centri matrice: DBT_RT/LaRIST_(2010_2012) - Edifici: DBT_RT/LaRIST_(2010_2012); BD_Catastale_AdT_(2012) - Percorsi fondativi: CIST_(2013) - Viabilita': DataBaseTopografico_Regione Toscana_(2000_2010); OpenStreetMap_(2012) - Linee ferroviarie: DBT_RT_(2000_2010) -) - Infrastrutture e attrezzature: Fotointerpretazione da OFC_AGEA_RT_(2010) - Presidi fortificati: BD_UNISI - Cinte murarie: DBT_RT_(2000_2010) - Acquedotti storici: QC_PTC - Copertura del suolo: UCS_RT_(2007) - Sistemazioni di versante delle colture legnose permanenti: DBT_RT_(2000_2010) - Scoline: DBT_RT_(2000_2010) - Trama del mosaico colturale dei seminativi di pianura: DBT_RT_(2000_2010); UCS_RT_(2007); BD_Catastale_AdT_(2012)."
    ],
    [
        "rt_piapae.carta_dei_sistemi_morfogenetici.50k.ct.rt",
        "Carta dei sistemi morfogenetici 1:50.000",
        "Carta dei sistemi morfogenetici 1:50.000. Lo strato propone la carta dei caratteri morfogenetici del territorio toscano in scala 1:50.000. La carta e' il frutto dell'analisi e dell'elaborazione di strati informativi provenienti da fonti istituzionali o frutto di elaborazioni originali. La principale fonte informativa e' il SITA della Regione Toscana. La carta e' finalizzata alla rappresentazione dei caratteri morfogenetici del territorio toscano, ovvero degli elementi obiettivamente riconoscibili della struttura fisica del paesaggio, definiti da una combinazione dei fattori che presiedono allo sviluppo delle forme del rilievo (fattori strutturali, temporali e geologici). La procedura adottata per la realizzazione della carta si e' basata principalmente sull'utilizzazione del Continuum Geologico Regionale, scala 1:10.000, e su un processo di generalizzazione delle informazioni in essa contenuta e di analisi integrata delle informazioni provenienti anche da altre banche dati (idrologiche, idrogeologiche, pedologiche, etc.) secondo una metodologia ispirata al metodo dei land systems. Sulla base di analisi integrate, la fotointerpretazione del rilievo ha permesso infine l'individuazione di associazioni di forme ricorrenti, che caratterizzano ogni sistema morfogenetico."
    ],
    [
        "rt_piapae.carta_del_territorio_urbanizzato.50k.ct.rt",
        "Carta del territorio urbanizzato 1:50.000",
        "Lo strato propone la carta del territorio urbanizzato in scala 1:50000. La carta e' finalizzata a fornire un supporto operativo per distinguere cio' che puo' essere considerato territorio a tutti gli effetti urbanizzato, il cui riuso non comporta pertanto nuovo 'consumo' di suolo, dal territorio utilizzabile a fini agricoli o dotato di valenze ambientali. La Carta del Territorio Urbanizzato rappresenta una ipotesi di perimetrazione delle aree urbanizzate realizzata utilizzando un modello geo-statistico per la illustrazione del quale si rimanda al capitolo relativo alla metodologia generale della 3a Invariante a livello regionale. Allo stesso capitolo si rinvia per le specificazioni normative relative alla applicazione del metodo per la perimetrazione del territorio urbanizzato a livello comunale. Il modello geostatistico utilizzato per la costruzione della carta del territorio urbanizzato, fondato sugli indicatori di continuita' e densita' dell'urbanizzato, ha consentito di elaborare per ogni ambito di paesaggio una carta in scala 1/50000, che individua le aree a edificato continuo, identificandone indicativamente anche i tipi di tessuto. Questa scala, adottata nel Piano paesaggistico per le schede degli Ambiti di paesaggio, non consente assolutamente di trasferire meccanicamente i confini del territorio urbanizzato individuati dalla carta alle scale proprie dei piani strutturali; ha validita' dunque unicamente come quadro indicativo, rispetto al quale e' necessario un percorso di verifica, reinterpretazione e puntualizzazione nell'elaborazione degli strumenti urbanistici."
    ],
    [
        "rt_piapae.carta_della_rete_ecologica.50k.ct.rt",
        "Carta della rete ecologica 1:50.000",
        "Carta della rete ecologica 1:50.000. Lo strato propone la carta della rete ecologica della Toscana in scala 1:50000. La carta e' finalizzata alla evidenziazione degli elementi strutturali e funzionali della rete ecologica regionale. La redazione della carta e' il risultato di una sintesi e rielaborazione di numerose informazioni provenienti da fonti istituzionali e/o libere. La redazione della carta si e' basata su modelli di idoneita' ambientale dei diversi usi del suolo rispetto alle specie di Vertebrati focali, sensibili alla frammentazione, tipiche degli ecosistemi forestali o agropastorali. Le principali fasi di redazione della carta sono state: (i) definizione degli obiettivi di conservazione in relazione ai fattori di frammentazione che agiscono alla scala regionale; (ii) selezione della carta Corine Land Cover IV livello, anno 2006 (scala 1:100.000); (iii) rilievo fotogrammetrico (fotogrammi anno 2010-AGEA-RT) per rilevare la presenza e ampiezza della vegetazione ripariale lungo le aste fluviali principali e integrazione dello strato informativo con il CLC 2006; (iv) elaborazione dei modelli di idoneita' ambientale (con procedura GLM) per le guilds di specie focali, previa rasterizzazione e generalizzazione del CLC2006 e utilizzo di altre banche dati (Tipi Climatici_RT e Inventario Forestale Toscano_RT); (v) trasposizione del valore di idoneita' dalle celle raster ai poligoni della carta vettoriale CLC 2006; (vi) definizione degli elementi strutturali delle reti; (vii) trasposizione del valore di idoneita' dei poligoni CLC 2006 allo strato informativo relativo all'uso del suolo della regione Toscana generalizzato in scala 1:50.000 (viii) individuazione degli elementi funzionali della rete ecologica."
    ],
    [
        "rt_piapae.parco_agricolo_piana_pit",
        "Parco agricolo della Piana - PIT - Salvaguardia A",
        "Parco Agricolo della Piana - PIT"
    ],
    [
        "rt_piapae.costa_fittizia",
        "Costa fittizia",
        "Strato vettoriale riportante la costa fittizia impiegata per la realizzazione del dataset della 'lettera a'"
    ]
];

const pianiOperativiArray = [
    ['Piani Operativi', []],
    ['Piani Operativi', 'Greve in Chianti', ['po:puc_po_greve_in_chianti', 'po:pat_po_greve_in_chianti']],
    ['Piani Operativi', 'Montemurlo', ['po:ned_po_montemurlo', 'po:puc_po_montemurlo', 'po:rig_po_montemurlo', 'po:pat_po_montemurlo']],
    ['Piani Operativi', 'Quarrata', ['po:ned_po_quarrata', 'po:puc_po_quarrata', 'po:rig_po_quarrata', 'po:pat_po_quarrata']],
    ['Piani Operativi', 'Scandicci', ['po:ned_po_scandicci', 'po:puc_po_scandicci', 'po:pat_po_scandicci']],
    ['Piani Operativi', 'Vaglia', ['po:ned_po_vaglia', 'po:puc_po_vaglia', 'po:pat_po_vaglia']],
    ['Piani Operativi', 'Vicchio', ['po:puc_po_vicchio', 'po:pat_po_vicchio']]
];

const pianiStrutturaliArray = [
    ['Piani Strutturali', []],

    ['Piani Strutturali', 'PSI Sesto Calenzano', []],
    ['Piani Strutturali', 'PSI Sesto Calenzano', 'Calenzano', ['ps:tu_ps_calenzano']],
    ['Piani Strutturali', 'PSI Sesto Calenzano', 'Sesto F.no', ['ps:tu_ps_sesto_fiorentino']],
    ['Piani Strutturali', 'PSI Media Valle Serchio', []],
    ['Piani Strutturali', 'PSI Media Valle Serchio', 'Bagni di Lucca', ['ps:tu_ps_bagni_di_lucca']],
    ['Piani Strutturali', 'PSI Media Valle Serchio', 'Barga', ['ps:tu_ps_barga']],
    ['Piani Strutturali', 'PSI Media Valle Serchio', 'Borgo a Mozzano', ['ps:tu_ps_borgo_a_mozzano']],
    ['Piani Strutturali', 'PSI Media Valle Serchio', 'Coreglia Antelm.', ['ps:tu_ps_coreglia_antelminelli']],
    ['Piani Strutturali', 'PSI Media Valle Serchio', 'Pescaglia', ['ps:tu_ps_pescaglia']],

    ['Piani Strutturali', 'PSI Garfagnana', []],
    ['Piani Strutturali', 'PSI Garfagnana', 'Camporgiano', ['ps:tu_ps_camporgiano']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Careggine', ['ps:tu_ps_careggine']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Castelnuovo G.na', ['ps:tu_ps_castelnuovo_garfagnana']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Castiglione G.na', ['ps:tu_ps_castiglione_garfagnana']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Fabbriche Vergemoli', ['ps:tu_ps_fabbriche_vergemoli']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Fosciandora', ['ps:tu_ps_fosciandora']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Gallicano', ['ps:tu_ps_gallicano']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Minucciano', ['ps:tu_ps_minucciano']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Molazzana', ['ps:tu_ps_molazzana']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Piazza al Serchio', ['ps:tu_ps_piazza_al_serchio']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Pieve Fosciana', ['ps:tu_ps_pieve_fosciana']],
    ['Piani Strutturali', 'PSI Garfagnana', 'San Romano G.na', ['ps:tu_ps_san_romano_garfagnana']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Sillano Giuncugnano', ['ps:tu_ps_sillano_giuncugnano']],
    ['Piani Strutturali', 'PSI Garfagnana', 'Villa Colemandina', ['ps:tu_ps_villa_collemandina']],

    ['Piani Strutturali', 'PSI Marciano Lucignano', []],
    ['Piani Strutturali', 'PSI Marciano Lucignano', 'Lucignano', ['ps:tu_ps_lucignano']],
    ['Piani Strutturali', 'PSI Marciano Lucignano', 'Marciano Chiana', ['ps:tu_ps_marciano_della_chiana']],

    ['Piani Strutturali', 'Camaiore', ['ps:tu_ps_camaiore']],
    ['Piani Strutturali', 'Caciana T. - Lari', ['ps:tu_ps_cascina_terme_lari']],
    ['Piani Strutturali', 'Civitella Val di Chiana', ['ps:tu_ps_civitella_val_di_chiana']],
    ['Piani Strutturali', 'Cutigliano', ['ps:tu_ps_cutigliano']],
    ['Piani Strutturali', 'Figline Incisa', ['ps:tu_ps_figline_incisa_valdarno']],
    ['Piani Strutturali', 'Greve in Chianti', ['ps:tu_ps_greve_in_chianti']],
    ['Piani Strutturali', 'Lastra a Signa', ['ps:tu_ps_lastra_a_signa']],
    ['Piani Strutturali', 'Livorno', ['ps:tu_ps_livorno']],
    ['Piani Strutturali', 'Lucca', ['ps:tu_ps_lucca']],
    ['Piani Strutturali', 'Montecarlo', ['ps:tu_ps_montecarlo']],
    ['Piani Strutturali', 'Montemurlo', ['ps:tu_ps_montemurlo']],
    ['Piani Strutturali', 'Montignoso', ['ps:tu_ps_montignoso']],
    ['Piani Strutturali', 'Peccioli', ['ps:tu_ps_peccioli']],
    ['Piani Strutturali', 'Piancastagnaio', ['ps:tu_ps_piancastagnaio']],
    ['Piani Strutturali', 'Quarrata', ['ps:tu_ps_quarrata']],
    ['Piani Strutturali', 'Reggello', ['ps:tu_ps_reggello']],
    ['Piani Strutturali', 'Scandicci', ['ps:tu_ps_scandicci']],
    ['Piani Strutturali', 'Vicchio', ['ps:tu_ps_vicchio']],
    ['Piani Strutturali', 'Vagli di Sotto', ['ps:tu_ps_vagli_di_sotto']],
    ['Piani Strutturali', 'Fiesole', ['ps:tu_ps_fiesole']],
    ['Piani Strutturali', 'Forte dei Marmi', ['ps:tu_ps_forte_dei_marmi']],
    ['Piani Strutturali', 'Vaglia', ['ps:tu_ps_vaglia']]
];

const invariantiArray = [
    ['Invarianti', []],
    ['Invarianti', 'Pozzi', ['invarianti:pozzi']],
    ['Invarianti', 'Sottosistemi morfogenetici ', ['invarianti:sottosistemi_morfogenetici_ssm']],
    ['Invarianti', 'Crinali ', ['invarianti:crinali']],
    ['Invarianti', 'Aree di margine', ['invarianti:aree_di_margine_conoidi_terrazzi']],
    ['Invarianti', 'Bacini neogenici', ['invarianti:Bacini_Neogenici-calanchi_biancane_balze', 'invarianti:bacini_neogenici_calanchi_biancane_balze_II', 'invarianti:Bacini_Neogenici-calanchi_biancane_balze_III']],
    ['Invarianti', 'Rete colture agrarie', ['invarianti:prati_stabili', 'invarianti:colture_arboree_specializzate', 'invarianti:colture_in_abbandono', 'invarianti:olivo']],
    ['Invarianti', 'Rete viaria', ['invarianti:strade_campestri', 'invarianti:sentieri_mulattiere', 'invarianti:percorsi_fondativi', 'invarianti:strade_50k']],
    
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', []],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Idrografia', ['invarianti:reticolo_idrologico', 'invarianti:rete_idraulico_agraria', 'invarianti:scoline', 'invarianti:corsi_acqua_areali']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Aree boscate', ['invarianti:aree_boscate']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Rete siepi', ['invarianti:rete_siepi', 'invarianti:vegetazione_evoluzione']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Rete muretti a secco', ['invarianti:rete_muretti_secco']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Rete praterie', ['invarianti:rete_praterie_radure']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Capacità uso dei suoli', ['invarianti:lcc', 'invarianti:fertilità']],
    ['Invarianti', 'Categoria_A_continua (DGR 1148/2002)', 'Limitazioni del suoli', ['invarianti:erosione', 'invarianti:deficit_idrico']],

    ['Invarianti', 'Categoria_B_discontinua (DGR 1148/2002)', []],
    ['Invarianti', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete alberi isolati', ['invarianti:rete_alberi_isolati']],
    ['Invarianti', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete pozze', ['invarianti:rete_pozze']],
    ['Invarianti', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete aree umide', ['invarianti:aree_umide']]
];

const parseLayersArrays = (layersArray) => {
    return layersArray.reduce((acc, entry) => {
        const layersNames = entry[entry.length - 1];
        const groupPath = entry.filter((val, idx) => idx < entry.length - 1);
        const groupTitle = groupPath[groupPath.length - 1];
        const group = groupPath
            .map(str => snakeCase(str.replace(/\.|\-|\(|\)\//g, ''))).join('.')
        return {
            groups: [
                ...acc.groups,
                {
                    "id": group,
                    "title": groupTitle, 
                    "expanded": true
                }
            ],
            layers: [
                ...acc.layers,
                ...layersNames.map((name) => ({
                    name,
                    group
                }))
            ]
        };
    }, { groups: [], layers: []});
}

/*
dev tool to create static maps
import this epic in the app to print out
layers and group structure based on the above configuration
*/
const getLayersCapabilities = (layersArray, text) =>{

    const { layers, groups } = parseLayersArrays(layersArray);
    return Promise.all([
        ...layers.reverse().map((l) =>
            wms.getLayerCapabilities({ url: '/geoserver/wms', ...l })
                .toPromise()
                .then((cap) => ({ ...cap, ...l })))
    ]).then((capabilities) => {
        const layersObjs = capabilities.map((layer) => {
            return {
                "type": "wms",
                "format": "image/png",
                "url": "/geoserver/wms",
                "visibility": false,
                "group": layer.group,
                "name": layer.name,
                "title": layer.title,
                "description": layer._abstract,
                "bbox": {
                    "crs": "EPSG:4326",
                    "bounds": {
                        "minx": layer?.exGeographicBoundingBox?.westBoundLongitude,
                        "miny": layer?.exGeographicBoundingBox?.southBoundLatitude,
                        "maxx": layer?.exGeographicBoundingBox?.eastBoundLongitude,
                        "maxy": layer?.exGeographicBoundingBox?.northBoundLatitude,
                    }
                },
                "allowedSRS": {
                    "EPSG:3003": true,
                    "EPSG:3785": true,
                    "EPSG:3857": true,
                    "EPSG:4269": true,
                    "EPSG:4326": true,
                    "EPSG:6707": true,
                    "EPSG:102113": true,
                    "EPSG:900913": true
                },
                "search": {
                    "url": "/geoserver/wfs",
                    "type": "wfs"
                }
            };
        });
        console.log(text);
        console.log('Layers', JSON.stringify(layersObjs));
        console.log('Groups', JSON.stringify(groups));
    })
}


export const printLayersOfPianiOperativi = () => {
    getLayersCapabilities(pianiOperativiArray, 'layers/piani_operativi.json');
}

export const printLayersOfPianiStutturali = () => {
    getLayersCapabilities(pianiStrutturaliArray, 'layers/piani_strutturali.json');
}

export const printLayersOfInvarianti = () => {
    getLayersCapabilities(invariantiArray, 'layers/invarianti.json');
}

export const printLayersOfPianoPaesaggisticoRegionale = () => {
    const pPR = pianoPaesaggisticoRegionaleArray.reverse().map(([name, title, desc]) => ({
        "type": "wms",
        "format": "image/png",
        "url": "http://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms",
        "visibility": false,
        "group": "piano_paesaggistico_regionale",
        "name": name,
        "title": title,
        "description": desc,
        "params": {
            "map": "wmspiapae",
            "map_resolution": 91
        },
        "bbox": {
            "crs": "EPSG:4326",
            "bounds": {
                "minx": 9.664338414951173,
                "miny": 42.21054230277022,
                "maxx": 12.411684664287653,
                "maxy": 44.47372015451805
            }
        }
    }));
    console.log('layers/piano_paesaggistico_regionale.json');
    console.log('Layers', JSON.stringify(pPR));
    console.log('Groups', JSON.stringify([
        {
            "id": "piano_paesaggistico_regionale",
            "title": "Piano paesaggistico regionale",
            "expanded": true
        }
    ]));
}

function addParamsToLayers(layers, params) {
    return layers.map(layer => ({
        ...layer,
        visibility: false,
        format: 'image/png8',
        tileSize: 512,
        ...params
    }));
}

export const printStaticMaps = () => {
    // mappa_piani_operativi.json
    console.log('mappa_piani_operativi.json');
    console.log(
        JSON.stringify(
            mappaBase(
                [
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers, { format: 'image/png' }),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers)
                ],
                [
                    ...pianoPaesaggisticoRegionale.groups,
                    ...invarianti.groups,
                    ...pianiStrutturali.groups,
                    ...pianiOperativi.groups
                ]
            )
        )
    );
    // mappa_piani_strutturali.json
    console.log('mappa_piani_strutturali.json');
    console.log(
        JSON.stringify(
            mappaBase(
                [
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers, { format: 'image/png' }),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers)
                ],
                [
                    ...pianoPaesaggisticoRegionale.groups,
                    ...invarianti.groups,
                    ...pianiStrutturali.groups,
                    ...pianiOperativi.groups
                ]
            )
        )
    );
}
