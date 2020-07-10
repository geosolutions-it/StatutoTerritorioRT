/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import expect from 'expect';
import {
    enableCatalogSerapide,
    selectCatalogEntrySerapide,
    loadingDataSerapide,
    updateCatalogResultsSerapide,
    errorCatalogResultsSerapide
} from '../../actions/serapide';
import serapide from '../serapide';

describe('serapide reducers', () => {
    it('test enableCatalogSerapide', () => {
        const enabled = true;
        const state = serapide({}, enableCatalogSerapide(enabled));
        expect(state.enabled).toBe(true);
    });
    it('test selectCatalogEntrySerapide', () => {
        const selected = { id: 'c_2' };
        const state = serapide({}, selectCatalogEntrySerapide(selected));
        expect(state.selected).toEqual(selected);
    });
    it('test loadingDataSerapide', () => {
        const loading = true;
        const state = serapide({}, loadingDataSerapide(loading));
        expect(state.loading).toBe(loading);
    });
    it('test updateCatalogResultsSerapide', () => {
        const response = {
            totalCount: 1,
            page: 1,
            results: [{
                comune: 'Comune',
                id: 'c_2',
                lastUpdate: '2020-07-07T14:31:57.441Z',
                name: 'Name',
                type: 'OPERATIVO'
            }]
        };
        const state = serapide({}, updateCatalogResultsSerapide(response));
        expect(state.error).toBe(false);
        expect(state.results).toEqual(response.results);
        expect(state.totalCount).toBe(response.totalCount);
        expect(state.page).toBe(response.page);
    });
    it('test loadingDataSerapide', () => {
        const error = true;
        const state = serapide({}, errorCatalogResultsSerapide(error));
        expect(state.error).toBe(error);
    });
});


