/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import expect from 'expect';
import {
    requestSerapideData,
    requestSerapideDataById,
    getSerapideGroups
} from '../index';
import axios from '@mapstore/libs/ajax';
import MockAdapter from "axios-mock-adapter";

let mockAxios;

describe('Serapide APIs', () => {

    beforeEach(done => {
        mockAxios = new MockAdapter(axios);
        setTimeout(done);
    });

    afterEach(done => {
        mockAxios.restore();
        setTimeout(done);
    });

    it('requestSerapideData', done => {
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
        mockAxios.onGet()
            .reply((config) => {
                try {
                    expect(config.params.q).toBe('text');
                    expect(config.params.page).toBe(1);
                    expect(config.params.limit).toBe(12);
                } catch (e) {
                    done(e);
                }
                return [ 200, data];
            });
        const params = {
            q: 'text',
            limit: 12,
            page: 1
        };
        requestSerapideData(params)
            .then(response => {
                expect(response).toEqual(data);
                done();
            });
    });

    it('requestSerapideDataById', done => {
        const data = {
            comune: 'Comune',
            id: 'c_2',
            lastUpdate: '2020-07-07T14:31:57.441Z',
            name: 'Name',
            type: 'OPERATIVO',
            map: { layers: [] }
        };
        mockAxios.onGet()
            .reply(() => {
                return [ 200, data];
            });
        const id = 2;
        requestSerapideDataById(id)
            .then(response => {
                expect(response).toEqual(data);
                done();
            });
    });

    it('getSerapideGroups', done => {
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
        getSerapideGroups()
            .then(response => {
                expect(response).toEqual([{
                    id: 'piano',
                    title: 'Piano',
                    expanded: true
                }, {
                    id: 'piano.validazione_cartografia_adozione',
                    title: 'Adottato',
                    expanded: true,
                    parent: 'piano'
                }]);
                done();
            });
    });

    it('getSerapideGroups with error', done => {
        mockAxios.onGet()
            .reply(404);
        getSerapideGroups()
            .then(response => {
                expect(response).toEqual([]);
                done();
            });
    });

});
