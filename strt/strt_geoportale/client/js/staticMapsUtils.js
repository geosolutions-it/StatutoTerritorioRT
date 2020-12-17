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
import risorse from '../static/mapstore/layers/risorse.json';
import axios from '@mapstore/libs/ajax';
import xml2js from 'xml2js';

function getCap({
    wmsUrl,
    mapParam,
    mapResolution
}) {
    return axios.get(`${wmsUrl}?map=${mapParam}&SERVICE=WMS&REQUEST=GetCapabilities`)
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
            const layers = Layer?.Layer.map((Lyr) => {
                const bbox = Lyr.EX_GeographicBoundingBox[0];
                return {
                    "type": "wms",
                    "format": format,
                    "url": wmsUrl,
                    "visibility": false,
                    "name": Lyr.Name[0],
                    "title": Lyr.Title[0],
                    "description": Lyr.Abstract[0],
                    "params": {
                        "map": mapParam,
                        "map_resolution": mapResolution
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
                    allowedSRS
                };
            });
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
    ]]
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
    getCap({
        wmsUrl: 'https://www502.regione.toscana.it/wmsraster/com.rt.wms.RTmap/wms',
        mapParam: 'wmsarprot',
        mapResolution: 91
    }).then((capLayers) => {
        const newLayers = layers.reverse().map((layer) => {
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
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers),
                    ...addParamsToLayers(risorse.layers),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers),
                ],
                [
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
                    ...addParamsToLayers(pianoPaesaggisticoRegionale.layers),
                    ...addParamsToLayers(risorse.layers),
                    ...addParamsToLayers(invarianti.layers),
                    ...addParamsToLayers(pianiStrutturali.layers),
                    ...addParamsToLayers(pianiOperativi.layers)
                ],
                [
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
