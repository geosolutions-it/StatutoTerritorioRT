/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import expect from 'expect';
import { testEpic } from '@mapstore/epics/__tests__/epicTestUtils';
import {
    strtAddMapConfigurations,
    strtSearchSerapide,
    strtSelectCatalogEntrySerapide
} from '../serapide';
import { configureMap } from '@mapstore/actions/config';
import { ZOOM_TO_EXTENT } from '@mapstore/actions/map';
import {
    ADD_GROUP,
    MOVE_NODE,
    REMOVE_LAYER,
    ADD_LAYER,
    UPDATE_NODE
} from '@mapstore/actions/layers';
import { SHOW_NOTIFICATION } from '@mapstore/actions/notifications';
import {
    SELECT_CATALOG_ENTRY_SERAPIDE,
    LOADING_DATA_SERAPIDE,
    ERROR_CATALOG_RESULTS_SERAPIDE,
    UPDATE_CATALOG_RESULTS_SERAPIDE,
    searchSerapide,
    selectCatalogEntrySerapide
} from '@js/actions/serapide';
import {
    setDefaultGroupsIds
} from '@js/utils/GeoportaleUtils';
import axios from '@mapstore/libs/ajax';
import MockAdapter from "axios-mock-adapter";

let mockAxios;

describe('serapide epics', function() {

    beforeEach(done => {
        mockAxios = new MockAdapter(axios);
        setTimeout(done);
    });

    afterEach(done => {
        mockAxios.restore();
        setDefaultGroupsIds([]);
        setTimeout(done);
    });

    it('strtAddMapConfigurations', function(done) {

        const state = {
            router: {
                location: {
                    search: '?s_uid=c_2'
                }
            }
        };

        const data = {
            groups: [{
                id: "validazione_cartografia_adozione",
                title: "Adottato"
            }]
        };
        mockAxios.onGet()
            .reply(() => {
                return [ 200, data];
            });

        const NUMBER_OF_ACTIONS = 4;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    ADD_GROUP,
                    ADD_GROUP,
                    MOVE_NODE,
                    SELECT_CATALOG_ENTRY_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };

        testEpic(
            strtAddMapConfigurations,
            NUMBER_OF_ACTIONS,
            configureMap(),
            callback,
            state);
    });
    it('strtSearchSerapide with error on groups request', function(done) {

        const state = {
            router: {
                location: {
                    search: '?s_uid=c_2'
                }
            }
        };

        mockAxios.onGet().reply(404);

        const NUMBER_OF_ACTIONS = 2;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    MOVE_NODE,
                    SELECT_CATALOG_ENTRY_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };

        testEpic(
            strtAddMapConfigurations,
            NUMBER_OF_ACTIONS,
            configureMap(),
            callback,
            state);
    });
    it('strtSearchSerapide', function(done) {

        const state = {};

        const data = {
            page: 1,
            totalCount: 1,
            results: [{
                comune: 'Comune',
                id: 'c_2',
                lastUpdate: '2020-07-07T14:31:57.441Z',
                name: 'Name',
                type: 'OPERATIVO'
            }]
        };

        mockAxios.onGet().reply(() => [ 200, data]);

        const NUMBER_OF_ACTIONS = 4;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    LOADING_DATA_SERAPIDE,
                    ERROR_CATALOG_RESULTS_SERAPIDE,
                    UPDATE_CATALOG_RESULTS_SERAPIDE,
                    LOADING_DATA_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };

        const params = {
            q: '',
            limit: 12,
            page: 1
        };
        testEpic(
            strtSearchSerapide,
            NUMBER_OF_ACTIONS,
            searchSerapide(params),
            callback,
            state);
    });
    it('strtSearchSerapide with error', function(done) {

        const state = {};

        mockAxios.onGet().reply(400);

        const NUMBER_OF_ACTIONS = 4;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    LOADING_DATA_SERAPIDE,
                    ERROR_CATALOG_RESULTS_SERAPIDE,
                    LOADING_DATA_SERAPIDE,
                    ERROR_CATALOG_RESULTS_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };
        const params = {
            q: '',
            limit: 12,
            page: 1
        };
        testEpic(
            strtSearchSerapide,
            NUMBER_OF_ACTIONS,
            searchSerapide(params),
            callback,
            state);
    });

    it('strtSelectCatalogEntrySerapide', function(done) {

        setDefaultGroupsIds(['piano']);

        const state = {
            layers: {
                flat: [{
                    group: 'piano'
                }]
            }
        };

        const data = {
            comune: 'Comune',
            id: 'c_2',
            lastUpdate: '2020-07-07T14:31:57.441Z',
            name: 'Name',
            type: 'OPERATIVO',
            map: { layers: [
                {
                    group: 'piano.approvazione',
                    bbox: {
                        bounds: {
                            minx: -180,
                            miny: -90,
                            maxx: 180,
                            maxy: 90
                        },
                        crs: 'EPSG:4326'
                    }
                }
            ] }
        };
        mockAxios.onGet()
            .reply(() => {
                return [ 200, data];
            });

        const NUMBER_OF_ACTIONS = 7;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    '@@router/CALL_HISTORY_METHOD',
                    LOADING_DATA_SERAPIDE,
                    ZOOM_TO_EXTENT,
                    REMOVE_LAYER,
                    ADD_LAYER,
                    UPDATE_NODE,
                    LOADING_DATA_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };
        const selected = {
            id: 'c_2'
        };
        testEpic(
            strtSelectCatalogEntrySerapide,
            NUMBER_OF_ACTIONS,
            selectCatalogEntrySerapide(selected),
            callback,
            state);
    });

    it('strtSelectCatalogEntrySerapide with error', function(done) {

        const state = {};

        mockAxios.onGet().reply(404);

        const NUMBER_OF_ACTIONS = 4;

        const callback = (actions) => {
            try {
                expect(actions.map(({ type }) => type)).toEqual([
                    '@@router/CALL_HISTORY_METHOD',
                    LOADING_DATA_SERAPIDE,
                    SHOW_NOTIFICATION,
                    LOADING_DATA_SERAPIDE
                ]);
            } catch (e) {
                done(e);
            }
            done();
        };
        const selected = {
            id: 'c_2'
        };
        testEpic(
            strtSelectCatalogEntrySerapide,
            NUMBER_OF_ACTIONS,
            selectCatalogEntrySerapide(selected),
            callback,
            state);
    });
});


