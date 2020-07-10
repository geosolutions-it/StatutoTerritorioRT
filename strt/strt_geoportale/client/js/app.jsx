/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import ConfigUtils from '@mapstore/utils/ConfigUtils';
import axios from '@mapstore/libs/ajax';

// list of path that need version parameter
const pathsNeedVersion = [
    'localConfig.json',
    '/translations/',
    'map.json'
];

const version = process.env.NODE_ENV === 'production' ? __MS_VERSION__ : '';

axios.interceptors.request.use(
    config => {
        if (config.url && version && pathsNeedVersion.filter(url => config.url.match(url))[0]) {
            return {
                ...config,
                params: {
                    ...config.params,
                    version
                }
            };
        }
        return config;
    }
);


// Fix mapLayout

ConfigUtils.setConfigProp('mapLayout', { left: { sm: 300, md: 500, lg: 600 }, right: { md: 658 }, bottom: { sm: 30 } });

/**
 * Add custom (overriding) translations with:
 *
 * ConfigUtils.setConfigProp('translationsPath', ['./MapStore2/web/client/translations', './translations']);
 */
ConfigUtils.setConfigProp('translationsPath', ['/static/mapstore/MapStore2/web/client/translations', '/static/mapstore/translations']);
ConfigUtils.setConfigProp('themePrefix', 'Geoportale');

/**
 * Use a custom plugins configuration file with:
 *
 * ConfigUtils.setLocalConfigurationFile('localConfig.json');
 */
ConfigUtils.setLocalConfigurationFile('/static/mapstore/localConfig.json');

/**
 * Use a custom application configuration file with:
 *
 * const appConfig = require('./appConfig');
 *
 * Or override the application configuration file with (e.g. only one page with a mapviewer):
 *
 * const appConfig = assign({}, require('@mapstore/product/appConfig'), {
 *     pages: [{
 *         name: "mapviewer",
 *         path: "/",
 *         component: require('@mapstore/product/pages/MapViewer')
 *     }]
 * });
 */
import appConfig from '@mapstore/product/appConfig';

/**
 * Define a custom list of plugins with:
 *
 * const plugins = require('./plugins');
 */
import plugins from './plugins';

import main from '@mapstore/product/main';
import appEpics from '@js/epics/app';

import { loadVersion } from '@mapstore/actions/version';

main({
    ...appConfig, pages: [{
        name: "home",
        path: "/",
        component: require('@mapstore/product/pages/Maps')
    }, {
        name: "maps",
        path: "/maps",
        component: require('@mapstore/product/pages/Maps')
    }, {
        name: "mapviewer",
        path: "/viewer/:mapType/:mapId",
        component: require('@mapstore/product/pages/MapViewer')
    }, {
        name: "mapviewer",
        path: "/viewer/:mapId",
        component: require('@mapstore/product/pages/MapViewer')
    }], themeCfg: { path: '/static/mapstore/themes', prefixContainer: '#geoportale' },
    appEpics
}, plugins, cfg => ({
    ...cfg,
    enableExtensions: false,
    initialActions: [
        loadVersion.bind(null, '/static/mapstore/version.txt')
    ]
}));
