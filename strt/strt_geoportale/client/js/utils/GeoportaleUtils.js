/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import { reprojectBbox } from '@mapstore/utils/CoordinatesUtils';

export const ID_PARAM = 's_uid';

let DEFAULT_GROUPS_IDS = [];

export const setDefaultGroupsIds = (groupsIds) => {
    DEFAULT_GROUPS_IDS = groupsIds;
};

export const getDefaultGroupsIds = () => DEFAULT_GROUPS_IDS;

export const getMapUrl = (params) => {
    return `/viewer/${params.mapId || 'map'}?${ID_PARAM}=${params.id}`;
};

export const get4326BBOX = (bbox) => {
    const { crs, bounds } = bbox || {};

    if (!crs || !bounds || crs === 'EPSG:4326' || crs === 'epsg:4326') {
        return bbox;
    }
    const [ minx, miny, maxx, maxy ] = reprojectBbox(bounds, crs, 'EPSG:4326') || [-180, -90, 180, 90];
    return {
        crs: 'EPSG:4326',
        bounds: {
            minx,
            miny,
            maxx,
            maxy
        }
    };
};

export const mergeLayersBBOXs = (layers = []) => {
    const layersBbox = layers.filter(layer => layer.bbox).map(layer => layer.bbox);
    if (layersBbox.length === 0) {
        return null;
    }
    const bbox = layersBbox.length > 1
        ? layersBbox.reduce((a, b) => {
            return {
                bounds: {
                    maxx: a.bounds.maxx > b.bounds.maxx ? a.bounds.maxx : b.bounds.maxx,
                    maxy: a.bounds.maxy > b.bounds.maxy ? a.bounds.maxy : b.bounds.maxy,
                    minx: a.bounds.minx < b.bounds.minx ? a.bounds.minx : b.bounds.minx,
                    miny: a.bounds.miny < b.bounds.miny ? a.bounds.miny : b.bounds.miny
                }, crs: b.crs};
        }, layersBbox[0])
        : layersBbox[0];
    return bbox;
};

export default {
    ID_PARAM,
    getMapUrl,
    get4326BBOX,
    mergeLayersBBOXs
};
