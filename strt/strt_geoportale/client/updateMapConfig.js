/**
 * Copyright 2021, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the ISC-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* eslint-disable */

const path = require('path');
const fs = require('fs');
const url = require('url');
const axios = require('axios');
const xml2js = require('xml2js');
const uniqBy = require('lodash/uniqBy');
const get = require('lodash/get');
const proj4 = require('proj4');

const startsWith = require('lodash/startsWith');
const mapsDirectory = path.join(__dirname, 'static', 'mapstore', 'maps');
const files = fs.readdirSync(mapsDirectory);

// MapStore2 utils/MapUtils.js
const DEFAULT_SCREEN_DPI = 96;
const METERS_PER_UNIT = {
    'm': 1,
    'degrees': 111194.87428468118,
    'ft': 0.3048,
    'us-ft': 1200 / 3937
};
const getUnits = function(projection) {
    const proj = new proj4.Proj(projection);
    return proj.units || 'degrees';
};
const dpi2dpm = (dpi) => {
    return dpi * (100 / 2.54);
};
const dpi2dpu = (dpi, projection) => {
    const units = getUnits(projection || 'EPSG:3857');
    return METERS_PER_UNIT[units] * dpi2dpm(dpi || DEFAULT_SCREEN_DPI);
};
// end MapStore2 utils/MapUtils.js

const getCapabilitiesUrl = (layer) => {
    const layerUrl = startsWith(layer.url, '/geoserver/')
        ? 'https://dev.serapide.geo-solutions.it' + layer.url
        : layer.url;
    return url.format({
        ...url.parse(layerUrl),
        query: {
            ...layer.params,
            SERVICE: 'WMS',
            REQUEST: 'GetCapabilities',
            VERSION: '1.3.0'
        }
    });
};


const DPU = dpi2dpu();

const updateLayer = (layer, capabilitiesOptions) => {
    if (capabilitiesOptions) {
        return {
            ...layer,
            ...capabilitiesOptions
        };
    }
    return layer;
};

const getCapabilitiesOptions = (layer, capabilities) => {
    const capabilitiesLayers = (get(capabilities.data, 'WMS_Capabilities.Capability[0].Layer[0].Layer') || [])
        .reduce((acc, capLayer) => {
            return [
                ...acc,
                capLayer,
                ...(capLayer.Layer || [])
            ];
        }, []);
    // const formats =  get(capabilities.data, 'WMS_Capabilities.Capability[0].Request[0].GetMap[0].Format');
    const capabilitiesLayer = capabilitiesLayers.find((capLayer) => {
        return capLayer.Name[0] === layer.name;
    });
    if (!capabilitiesLayer) {
        console.log('MISSING:LAYER_IN_CAPABILITIES', layer.name);
        return {};
    }

    const minScaleParam = capabilitiesLayer.MinScaleDenominator && {
        minScaleDenominator: parseFloat(capabilitiesLayer.MinScaleDenominator),
        minResolution: parseFloat(capabilitiesLayer.MinScaleDenominator) / DPU
    };
    const maxScaleParam = capabilitiesLayer.MaxScaleDenominator && {
        maxScaleDenominator: parseFloat(capabilitiesLayer.MaxScaleDenominator),
        maxResolution: parseFloat(capabilitiesLayer.MaxScaleDenominator) / DPU
    };
    return {
        ...minScaleParam,
        ...maxScaleParam
    };
};

const configurations = files.map((fileName) => [fileName, JSON.parse(fs.readFileSync(path.resolve(mapsDirectory, fileName), 'utf8')) || {}])

const capabilitiesUrls = uniqBy(configurations.reduce((acc, [fileName, { map }]) => {
    return [...acc, ...map.layers
        .filter((layer) => layer.url && layer.group !== 'background')
        .map((layer) => ({
            url: getCapabilitiesUrl(layer)
        }))];
}, []), 'url');

console.log('CAPABILITIES_REQUEST:START');
axios.all(
    capabilitiesUrls.map(capabilities =>
        axios.get(capabilities.url)
            .then(({ data }) => {
                let json;
                xml2js.parseString(data, {}, (ignore, result) => {
                    json = result;
                });
                return { ...capabilities, data: json };
            })
    )
).then((capabilities) => {
    console.log('CAPABILITIES_REQUEST:RESPONSE');
    configurations.forEach(([fileName, config]) => {
        console.log(`UPDATE_FILE:START ${fileName}`);
        const updatedConfiguration = {
            ...config,
            map: {
                ...config.map,
                layers: config.map.layers.map((layer) => {
                    if (layer.url && layer.group !== 'background') {
                        const capUrl = getCapabilitiesUrl(layer);
                        const layerCapabilities = capabilities.find((cap) => cap.url === capUrl);
                        if (!layerCapabilities) {
                            console.log('MISSING:LAYER_CAPABILITIES', layer.name);
                            return updateLayer(layer);
                        }
                        const capabilitiesOptions =  getCapabilitiesOptions(layer, layerCapabilities);
                        return updateLayer(layer, capabilitiesOptions);
                    }
                    console.log('MISSING:LAYER_URL', layer.name);
                    return updateLayer(layer);
                })
            }
        };

        fs.writeFile(
            path.resolve(mapsDirectory, fileName),
            JSON.stringify(updatedConfiguration, null, 4),
            function(err) {
                if (err) {
                    return console.log(err);
                }
                return console.log(`UPDATE_FILE:SUCCESS ${fileName}`);
            }
        );
    });
})
.catch((error) => {
    console.log('CAPABILITIES_REQUEST:ERROR', error);
});



