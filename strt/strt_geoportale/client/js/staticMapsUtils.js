/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import snakeCase from 'lodash/snakeCase';
import wms from '@mapstore/observables/wms';

import cartografiaDiBase from '../static/mapstore/layers/cartografia_di_base.json';
import invarianti from '../static/mapstore/layers/invarianti.json';
import pianiOperativi from '../static/mapstore/layers/piani_operativi.json';
import pianiStrutturali from '../static/mapstore/layers/piani_strutturali.json';
import pianoPaesaggisticoRegionale from '../static/mapstore/layers/piano_paesaggistico_regionale.json';
import risorse from '../static/mapstore/layers/risorse.json';
import axios from '@mapstore/libs/ajax';
import xml2js from 'xml2js';
import flatten from 'lodash/flatten';
import isObject from 'lodash/isObject';

function getCap({
    wmsUrl,
    mapParam,
    mapResolution,
    params
}) {
    return axios.get(wmsUrl, {
        params: {
            SERVICE: 'WMS',
            REQUEST: 'GetCapabilities',
            ...(mapParam && { map: mapParam }),
            ...params
        }
    })
        .then((response) => {
            let json;
            xml2js.parseString(response.data, {}, (ignore, result) => {
                json = result;
            });
            const Layer = json?.WMS_Capabilities?.Capability?.[0]?.Layer?.[0];
            const formats = json?.WMS_Capabilities?.Capability?.[0]?.Request?.[0]?.GetMap?.[0]?.Format;
            const allowedSRS = Layer?.CRS.reduce((acc, crs) => ({
                ...acc,
                [crs]: true
            }), {});
            const format = formats.indexOf('image/png8') !== -1
                ? 'image/png8'
                : formats.indexOf('image/png; mode=8bit') !== -1
                    ? 'image/png; mode=8bit'
                    : formats.indexOf('image/png') !== -1
                        ? 'image/png'
                        : formats[0];

            const getLayer = (Lyr) => {
                const bbox = Lyr.EX_GeographicBoundingBox[0];
                return {
                    "type": "wms",
                    "format": format,
                    "url": wmsUrl,
                    "visibility": false,
                    "name": Lyr.Name[0],
                    "title": Lyr.Title[0],
                    ...(Lyr?.Abstract?.[0] && { "description": Lyr?.Abstract?.[0]}),
                    "params": {
                        ...(mapParam && {"map": mapParam}),
                        ...(mapResolution && {"map_resolution": mapResolution}),
                        ...params
                    },
                    "bbox": {
                        "crs": "EPSG:4326",
                        "bounds": {
                            "minx": parseFloat(bbox.westBoundLongitude[0]),
                            "miny": parseFloat(bbox.southBoundLatitude[0]),
                            "maxx": parseFloat(bbox.eastBoundLongitude[0]),
                            "maxy": parseFloat(bbox.northBoundLatitude[0])
                        }
                    },
                    ...(Lyr.MinScaleDenominator && { "minScaleDenominator": parseFloat(Lyr.MinScaleDenominator)}),
                    ...(Lyr.MaxScaleDenominator && { "maxScaleDenominator": parseFloat(Lyr.MaxScaleDenominator) }),
                    // allowedSRS
                };
            }
            const layers = Layer?.Layer.reduce((acc, Lyr) => {
                if (Lyr?.Layer) {
                    return [
                        ...acc,
                        getLayer(Lyr),
                        ...Lyr.Layer.map((Ly) => getLayer(Ly))
                    ];
                }
                return [
                    ...acc,
                    getLayer(Lyr)
                ];
            }, []);
            return layers;
        });
}

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

const risorseArray = [
    ['Risorse', []],
    ['Risorse', 'Aria', []],
    ['Risorse', 'Aria', 'Inquinamento fisico', [
        'rt_inqfis.idpccaspt.rt',
        'rt_inqfis.idpccaspt.rt',
        'rt_inqfis.idpccaqua.rt',
        'rt_inqfis.idpccazon.rt',
        'rt_inqfis.idpcraarcrit_a.rt',
        'rt_inqfis.idpcrafru_l.rt',
        'rt_inqfis.idpcrairi_a.rt',
        'rt_inqfis.idpcrairi_l.rt',
        'rt_inqfis.idpcrairi_p.rt',
        'rt_inqfis.idpcrarcr_a.rt',
        'rt_inqfis.idpcramsf_p.rt',
        'rt_inqfis.stazioni_astronomiche.rt',
        'rt_inqfis.LR39_2005_art35_comma_1.rt',
        'rt_inqfis.LR39_2005_art35_comma_2.rt',
        'rt_inqfis.LR39_2005_art35_comma_4.rt'
    ]],
    ['Risorse', 'Clima', []],
    ['Risorse', 'Clima', 'Cumulata mensile delle precipitazioni in mm - (1995-2009)', [
        'PioggiaCum:Pcum_2009-M00',
        'PioggiaCum:Pcum_2009-M01',
        'PioggiaCum:Pcum_2009-M02',
        'PioggiaCum:Pcum_2009-M03',
        'PioggiaCum:Pcum_2009-M04',
        'PioggiaCum:Pcum_2009-M05',
        'PioggiaCum:Pcum_2009-M06',
        'PioggiaCum:Pcum_2009-M07',
        'PioggiaCum:Pcum_2009-M08',
        'PioggiaCum:Pcum_2009-M09',
        'PioggiaCum:Pcum_2009-M10',
        'PioggiaCum:Pcum_2009-M11',
        'PioggiaCum:Pcum_2009-M12'
    ]],
    ['Risorse', 'Clima', 'Media delle temperature massime del mese in °C - (1995-2009)', [
        'TempMax:Tmax_2009-M01',
        'TempMax:Tmax_2009-M02',
        'TempMax:Tmax_2009-M03',
        'TempMax:Tmax_2009-M04',
        'TempMax:Tmax_2009-M05',
        'TempMax:Tmax_2009-M06',
        'TempMax:Tmax_2009-M07',
        'TempMax:Tmax_2009-M08',
        'TempMax:Tmax_2009-M09',
        'TempMax:Tmax_2009-M10',
        'TempMax:Tmax_2009-M11',
        'TempMax:Tmax_2009-M12'
    ]],
    ['Risorse', 'Clima', 'Media delle temperature minime del mese in °C - (1995-2009)', [
        'TempMin:Tmin_2009-M01',
        'TempMin:Tmin_2009-M02',
        'TempMin:Tmin_2009-M03',
        'TempMin:Tmin_2009-M04',
        'TempMin:Tmin_2009-M05',
        'TempMin:Tmin_2009-M06',
        'TempMin:Tmin_2009-M07',
        'TempMin:Tmin_2009-M08',
        'TempMin:Tmin_2009-M09',
        'TempMin:Tmin_2009-M10',
        'TempMin:Tmin_2009-M11',
        'TempMin:Tmin_2009-M12'
    ]],
    ['Risorse', 'Clima', 'Numero giorni piovosi - (1995-2009)', [
        'PioggiaNum:Pnum_2009-M00',
        'PioggiaNum:Pnum_2009-M01',
        'PioggiaNum:Pnum_2009-M02',
        'PioggiaNum:Pnum_2009-M03',
        'PioggiaNum:Pnum_2009-M04',
        'PioggiaNum:Pnum_2009-M05',
        'PioggiaNum:Pnum_2009-M06',
        'PioggiaNum:Pnum_2009-M07',
        'PioggiaNum:Pnum_2009-M08',
        'PioggiaNum:Pnum_2009-M09',
        'PioggiaNum:Pnum_2009-M10',
        'PioggiaNum:Pnum_2009-M11',
        'PioggiaNum:Pnum_2009-M12'
    ]],
    ['Risorse', 'Acqua', []],
    ['Risorse', 'Acqua', 'RT difesa del suolo', [
        'comprensori_bonifica_10_06_2016',
        'reticolo_lr_79_2012',
        'reticolo_lr_79_2012'
    ]],
    ['Risorse', 'Suolo e sottosuolo', []],
    ['Risorse', 'Suolo e sottosuolo', 'Terremoti', [
        'rt_terremoti.eventi.cpti15',
        'rt_terremoti.eventi.ingv',
        'rt_terremoti.eventi.ingv.strumentali'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'Vincolo idrogeologico', [
        'rt_idrogeol.areeboscate.2016.rt.poly',
        'rt_idrogeol.areeboscate.2013.rt.poly',
        'rt_idrogeol.areeboscate.2010.rt.poly',
        'rt_idrogeol.areeboscate.2007.rt.poly',
        'rt_idrogeol.idrd32671923.rt.poly'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'DB geologico', [
        'rt_dbg.el_geol.unita_geologica_areale_100k',
        'rt_dbg.el_geol.unita_geologica_areale_10k',
        'rt_dbg.el_geol.limite_geologico'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'DB geomorfologico', [
        'FR - Frane',
        'FN - Frane Non Rappresentabili'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'Uso suolo', [
        'rt_ucs.iducs.10k.2016.rt.full'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'Pedologia', [
        'capacita_di_uso_e_fertilita_dei_suoli',
        'unita_di_paesaggio'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'Morfologia', [
        'rt_morfologia.iddtm.10m.rt',
        'rt_morfologia.dtm_10m_idrol.rt'
    ]],
    ['Risorse', 'Suolo e sottosuolo', 'Carsismo e speleologia', [
        'rt_carsismo_speleologia.idingrotte.point.rt',
        'rt_carsismo_speleologia.iddoline.point.rt',
        'rt_carsismo_speleologia.iddoline.poly.rt',
        'rt_carsismo_speleologia.idformecarsiche.point.rt',
        'rt_carsismo_speleologia.idformecarsiche.poly.rt',
        'rt_carsismo_speleologia.idsorgenticarsiche.point.rt',
        'rt_carsismo_speleologia.idareecarsificabili.poly.rt'
    ]],
    
    ['Risorse', 'Struttura ecosistemica', []],
    ['Risorse', 'Struttura ecosistemica', 'Biodiveristà', [
        'rt_arprot.idparnaz.rt.poly',
        'rt_arprot.idparnaz.rt.poly.dissolve',
        'rt_arprot.idpartoscoem.rt.poly',
        'rt_arprot.idparforcas.rt.poly',
        'rt_arprot.idpararctos.rt.poly',
        'rt_arprot.idrisnatstat.rt.poly',
        'rt_arprot.idareemarineprotette.rt.poly',
        'rt_arprot.idparreg.rt.poly',
        'rt_arprot.idparreg_alpiapuane.rt.poly',
        'rt_arprot.idparreg_maremma.rt.poly',
        'rt_arprot.idparreg_migliarino_sanrossore.rt.poly',
        'rt_arprot.idparprov.rt.poly',
        'rt_arprot.idrisnatprov.rt.poly',
        'rt_arprot.idanpil.rt.poly',
        'rt_arprot.idsir.rt.poly',
        'rt_arprot.idsir_sir.rt.poly',
        'rt_arprot.idnat2000_sic.rt.poly',
        'rt_arprot.idnat2000_zps.rt.poly',
        'rt_arprot.idnat2000_sic_zps.rt.poly',
        'rt_arprot.idramsar.rt.poly',
        'rt_arprot.id.pn.rns.pr.pp.rnp.rt.poly.dissolve',
        'rt_arprot.idgeotopi.rt.poly',
        'rt_arprot.renato.habitat.rt.point'
    ]],
    ['Risorse', 'Struttura ecosistemica', 'Flora', [
        'rt_arprot.idalbmon.rt.point',
        'rt_arprot.idalbmon_lr60_1998.rt.point',
        'rt_arprot.habitat_hascitu.rt',
        'rt_arprot.habitat_hascitu.rt.point.cod_zsc',
        'rt_arprot.habitat_hascitu.rt.point.code_priority',
        'rt_arprot.habitat_hascitu.rt.point.coribio',
        'rt_arprot.habitat_hascitu.rt.point.tipoveg',
        'rt_arprot.habitat_hascitu.rt.stampa',
        'rt_arprot.renato.specie.vegetali.rt.point',
        'rt_arprot.renato.fitocenosi.rt.point'
    ]],
    ['Risorse', 'Struttura ecosistemica', 'Fauna', [
        'rt_arprot.santuario_mammiferi_marini.rt',
        'rt_arprot.renato.specie.anfibi.rt.point',
        'rt_arprot.renato.specie.crostacei.rt.point',
        'rt_arprot.renato.specie.insetti.rt.point',
        'rt_arprot.renato.specie.mammiferi.rt.point',
        'rt_arprot.renato.specie.molluschi.rt.point',
        'rt_arprot.renato.specie.pesci.rt.point',
        'rt_arprot.renato.specie.rettili.rt.point',
        'rt_arprot.renato.specie.uccelli.rt.point'
    ]],
    ['Risorse', 'Struttura insediativa', []],

    ['Risorse', 'Struttura insediativa', 'Infrastrutture per la mobilità', [
        'rt_sent.idareecai.rt',
        'rt_sent.idsentcai.2005.rt',
        'rt_sent.idrifcai.2005.rt'
    ]],
    ['Risorse', 'Struttura insediativa', 'Popolazione (IRPET)', [
        'rt_amb_cens.centri_nuclei_2011',
        'rt_amb_cens.aree_prod_2011',
        'rt_amb_cens.centri_nuclei_2001',
        'rt_itnt.scuole.point.rt'
    ]],
    ['Risorse', 'Struttura insediativa', 'Processi socio-economici (IRPET)', [
        {
            "type": "link",
            "href": "http://territorio.irpet.it/#!/",
            "title": "Osservatorio territoriale"
        }
    ]],
    ['Risorse', 'Struttura insediativa', 'Salute umana', [
        'rt_itnt.presidisanitari.poly.rt',
        'rt_itnt.iarir_ul.poly.rt'
    ]],
    ['Risorse', 'Struttura insediativa', 'Energia', [
        'rt_rinnovabili.idzicv.rt',
        'rt_rinnovabili.idaadp.rt',
        'rt_rinnovabili.iddpadi.rt',
        'rt_rinnovabili.iddpadi.differenza.rt'
    ]],
    ['Risorse', 'Patrimonio culturale', []],
    ['Risorse', 'Patrimonio culturale', 'Documenti della cultura', [
        'rt_benicult.idpaesaggistico.rt',
        'rt_benicult.idarchitettonico.rt',
        'rt_benicult.idarcheologico.rt',
        'rt_opificistorici.opifici.point.rt',
        'rt_opificistorici.opifici.etichette.rt'
    ]],
];

const pianoPaesaggisticoRegionaleArray = [
    ['Piano paesaggistico regionale', [
        "rt_piapae.idambpae.rt.poly",
        "lett_a_artut",
        "lett_b_laghi",
        "specchi_acqua500m",
        "lett_c_aree_tutelate",
        "lett_c_fiumi",
        "rt_piapae.grafo.sistema.acque.rt",
        "lett_d_artut",
        "lett_e_artut",
        "rt_piapae.idparnaz.rt.poly",
        "rt_piapae.idrisnatstat.rt.poly",
        "rt_piapae.idparreg.rt.poly",
        "rt_piapae.idparprov.rt.poly",
        "rt_piapae.idrisnatprov.rt.poly",
        "lett_g_artut",
        "lett_g_artut_20150327_20181009",
        "lett_h_usicivici",
        "lett_i_artut",
        "lett_m_artut",
        "rt_piapae.vinc_archeo_ricad",
        "rt_piapae.vinc_archeo_coinc_1",
        "rt_piapae.vinc_archeo_coinc_2",
        "ulter_cont_unesco",
        "rt_piapae.idpae1_a.rt",
        "rt_piapae.idpae1_a_etichette.rt",
        "rt_piapae.topografica50k.color.rt",
        "rt_piapae.carta_dei_caratteri_del_paesaggio.50k.ct.rt",
        "rt_piapae.carta_dei_sistemi_morfogenetici.50k.ct.rt",
        "rt_piapae.carta_del_territorio_urbanizzato.50k.ct.rt",
        "rt_piapae.carta_della_rete_ecologica.50k.ct.rt",
        "rt_piapae.parco_agricolo_piana_pit",
        "rt_piapae.costa_fittizia",
    ]]
];

const cartografiaDiBaseArray = [
    ['Cartografia di base', []]
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
    ['Invarianti', 'Invariante I', []],
    ['Invarianti', 'Invariante I', 'Pozzi', ['invarianti:pozzi']],
    ['Invarianti', 'Invariante I', 'Sottosistemi morfogenetici ', ['invarianti:sottosistemi_morfogenetici_ssm']],
    ['Invarianti', 'Invariante I', 'Crinali ', ['invarianti:crinali']],
    ['Invarianti', 'Invariante I', 'Aree di margine', ['invarianti:aree_di_margine_conoidi_terrazzi', 'aree_di_margine_conoidi_terrazzi_II']],
    ['Invarianti', 'Invariante I', 'Bacini neogenici', ['invarianti:Bacini_Neogenici-calanchi_biancane_balze', 'invarianti:bacini_neogenici_calanchi_biancane_balze_II', 'invarianti:Bacini_Neogenici-calanchi_biancane_balze_III']],
    
    ['Invarianti', 'Invariante II', []],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', []],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Idrografia', ['invarianti:reticolo_idrologico', 'invarianti:rete_idraulico_agraria', 'invarianti:scoline', 'invarianti:corsi_acqua_areali']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Aree boscate', ['invarianti:aree_boscate']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Rete siepi', ['invarianti:rete_siepi', 'invarianti:vegetazione_evoluzione']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Rete muretti a secco', ['invarianti:rete_muretti_secco']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Rete praterie', ['invarianti:rete_praterie_radure']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Capacità uso dei suoli', ['invarianti:lcc', 'invarianti:fertilità']],
    ['Invarianti', 'Invariante II', 'Categoria_A_continua (DGR 1148/2002)', 'Limitazioni del suoli', ['invarianti:erosione', 'invarianti:deficit_idrico']],

    ['Invarianti', 'Invariante II', 'Categoria_B_discontinua (DGR 1148/2002)', []],
    ['Invarianti', 'Invariante II', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete alberi isolati', ['invarianti:rete_alberi_isolati']],
    ['Invarianti', 'Invariante II', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete pozze', ['invarianti:rete_pozze']],
    ['Invarianti', 'Invariante II', 'Categoria_B_discontinua (DGR 1148/2002)', 'Rete aree umide', ['invarianti:aree_umide']],

    ['Invarianti', 'Invariante IV', []],
    ['Invarianti', 'Invariante IV', 'Rete colture agrarie', ['invarianti:prati_stabili', 'invarianti:colture_arboree_specializzate', 'invarianti:colture_in_abbandono', 'invarianti:olivo']],
    ['Invarianti', 'Invariante IV', 'Rete viaria', ['invarianti:strade_campestri', 'invarianti:sentieri_mulattiere', 'invarianti:percorsi_fondativi', 'invarianti:strade_50k']],
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
                ...layersNames.map((name) => isObject(name)
                    ? { ...name, group }
                    : { name, group }
                )
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
                "format": "image/png8",
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

export const printLayersOfRisorse = () => {
    const { layers, groups } = parseLayersArrays(risorseArray);

    const risorseCaps = [
        {
            url: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsinqfis',
                map_resolution: 91
            }
        },
        {
            url: 'https://geoportale.lamma.rete.toscana.it/geoserver_clima/ows',
            params: {
                namespace: 'PioggiaCum'
            }
        },
        {
            url: 'https://geoportale.lamma.rete.toscana.it/geoserver_clima/ows',
            params: {
                namespace: 'TempMax'
            }
        },
        {
            url: 'https://geoportale.lamma.rete.toscana.it/geoserver_clima/ows',
            params: {
                namespace: 'TempMin'
            }
        },
        {
            url: 'https://geoportale.lamma.rete.toscana.it/geoserver_clima/ows',
            params: {
                namespace: 'PioggiaNum'
            }
        },
        {
            url: 'https://geoportale.lamma.rete.toscana.it/geoserver_ds/RETICOLO/ows'
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsterremoti',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsterremoti',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/geoscopio_qg/cgi-bin/qgis_mapserv',
            params: {
                map: 'dbgeologico_rt.qgs',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/geoscopio_qg/cgi-bin/qgis_mapserv',
            params: {
                map: 'dbgeomorfologico_rt.qgs',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsucs',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owspedologia',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsspeleologia',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsarprot',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsedificato',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows_infrastrutture_presidi/com.rt.wms.RTmap/ows',
            params: {
                map: 'owsinfrastrutturepresidi',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows_sentieristica/com.rt.wms.RTmap/wms',
            params: {
                map: 'owssentieristica',
                map_resolution: 91
            }
        },
    
        {
            url: 'https://www502.regione.toscana.it/cartografia/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsambcens',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows_infrastrutture_presidi/com.rt.wms.RTmap/ows',
            params: {
                map: 'owsinfrastrutturepresidi',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsrinnovabili',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows2/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsbenicult',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows_castore/com.rt.wms.RTmap/ows',
            params: {
                map: 'owsopificistorici',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/ows_idrogeologico/com.rt.wms.RTmap/wms',
            params: {
                map: 'owsidrogeologico',
                map_resolution: 91
            }
        },
        {
            url: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
            params: {
                map: 'wmsmorfologia',
                map_resolution: 91
            }
        }
    ]
    
    Promise.all(risorseCaps.map((res) =>
        getCap({
            wmsUrl: res.url,
            params: res.params
        })
            .then((capLayers) => {
                return capLayers;
            })
            .catch((err) => {
                console.log('ERROR', JSON.stringify(res), err);
                return null;
            })
    
    )).then(capLayersArray => {
        console.log(capLayersArray);
        const capLayers = flatten(capLayersArray);
        const newLayers = layers.reverse().map((layer) => {
            if (layer.type === 'link') {
                return layer;
            }
            const options = capLayers.find((capLayer) => capLayer.name === layer.name);
            if (!options) {
                console.log(layer.name, 'not found');
            }
            return { ...options, ...layer };
        });
        console.log('layers/risorse.json');
        console.log('Layers', JSON.stringify(newLayers));
        console.log('Groups', JSON.stringify(groups));
    });
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
    const { layers, groups } = parseLayersArrays(pianoPaesaggisticoRegionaleArray);
    getCap({
        wmsUrl: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
        mapParam: 'wmspiapae',
        mapResolution: 91
    }).then((capLayers) => {
        console.log('layers/piano_paesaggistico_regionale.json');
        const newLayers = layers.reverse().map((layer) => {
            const options = capLayers.find((capLayer) => capLayer.name === layer.name);
            if (!options) {
                console.log(layer.name, 'not found');
            }
            return { ...options, ...layer };
        });
        console.log('Layers', JSON.stringify(newLayers));
        console.log('Groups', JSON.stringify(groups));
    });
}

export const printLayersOfCartografiaDiBase = () => {
    const layers = [
        [
            'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms', // wmsUrl
            'wmsofc', // mapParam
            'rt_ofc.10k13', // layerName
            'Ortofoto 2013' // title
        ],
        [
            'https://www502.regione.toscana.it/ows_ofc/com.rt.wms.RTmap/wms', // wmsUrl
            'owsofc', // mapParam
            'rt_ofc.5k16.32bit', // layerName
            'Ortofoto 2016 20cm' // title
        ],
        [
            'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms', // wmsUrl
            'wmsambamm', // mapParam
            'rt_ambamm.idcomuni.rt.poly', // layerName
            'Confini comunali 2018' // title
        ],
        [
            'https://www502.regione.toscana.it/ows_ctr/com.rt.wms.RTmap/ows', // wmsUrl
            'owsctr', // mapParam
            'rt_ctr.10k_impianto', // layerName
            'CTR 1:10.000' // title
        ]
    ];
    Promise.all(
        layers.map(([ wmsUrl, mapParam, layerName, title ]) => getCap({
            wmsUrl,
            mapParam,
            mapResolution: 91
        }).then((capLayers) => {
            const layer = capLayers.find((capLayer) => capLayer.name === layerName);
            return {...layer, title, group: 'cartografia_di_base'}
        }))
    ).then((newLayers) => {
        const allLayers = [
            ...newLayers,
            {
                type: 'wms',
                url: 'https://www502.regione.toscana.it/geoscopio_qg/cgi-bin/qgis_mapserv',
                name: 'DBTM_DataBaseTopograficoMultiscala',
                title: 'DBT Multiscala',
                format: 'image/png; mode=8bit',
                group: 'cartografia_di_base',
                params: {
                    map: 'dbtm_rt.qgs',
                    map_resolution: 91
                }
            }
        ]
        const order = [
            'rt_ofc.10k13',
            'rt_ofc.5k16.32bit',
            'DBTM_DataBaseTopograficoMultiscala',
            'rt_ambamm.idcomuni.rt.poly',
            'rt_ctr.10k_impianto'
        ]
        console.log('Layers', JSON.stringify(order.reverse().map((name) => allLayers.find(layer => layer.name === name))));
        console.log('Groups', JSON.stringify([
            {
                "id": "cartografia_di_base",
                "title": "Cartografia di base",
                "expanded": true
            }
        ]));
    });
}

function addParamsToLayers(layers, params) {
    return layers.map(layer => ({
        ...layer,
        visibility: false,
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
                    ...addParamsToLayers(cartografiaDiBase.layers),
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers),
                    ...addParamsToLayers(risorse.layers),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers),
                ],
                [
                    ...cartografiaDiBase.groups,
                    ...pianoPaesaggisticoRegionale.groups,
                    ...risorse.groups,
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
                    ...addParamsToLayers(cartografiaDiBase.layers),
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers),
                    ...addParamsToLayers(risorse.layers),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers)
                ],
                [
                    ...cartografiaDiBase.groups,
                    ...pianoPaesaggisticoRegionale.groups,
                    ...risorse.groups,
                    ...invarianti.groups,
                    ...pianiStrutturali.groups,
                    ...pianiOperativi.groups
                ]
            )
        )
    );
}
