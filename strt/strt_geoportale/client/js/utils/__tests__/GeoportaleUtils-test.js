/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import expect from 'expect';
import {
    getMapUrl,
    mergeLayersBBOXs
} from '../GeoportaleUtils';

describe('GeoportaleUtils', () => {
    it('test getMapUrl', () => {
        const params = {
            mapId: 'config',
            id: 'c_2'
        };
        const mapUrl = getMapUrl(params);
        expect(mapUrl).toBe('/viewer/config?s_uid=c_2');
    });
    it('test getMapUrl with missing mapId (fallback to map config)', () => {
        const params = {
            id: 'c_2'
        };
        const mapUrl = getMapUrl(params);
        expect(mapUrl).toBe('/viewer/map?s_uid=c_2');
    });
    it('test mergeLayersBBOXs', () => {
        const layers = [
            {
                bbox: {
                    bounds: {
                        maxx: 44,
                        maxy: 38,
                        minx: 9,
                        miny: 16
                    }
                },
                crs: 'EPSG:4326'
            },
            {
                bbox: {
                    bounds: {
                        maxx: 45,
                        maxy: 37,
                        minx: 10,
                        miny: 15
                    }
                },
                crs: 'EPSG:4326'
            }
        ];
        const bbox = mergeLayersBBOXs(layers);
        expect(bbox.bounds).toEqual({
            maxx: 45,
            maxy: 38,
            minx: 9,
            miny: 15
        });
    });
});
