/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import expect from 'expect';
import { testEpic } from '@mapstore/epics/__tests__/epicTestUtils';
import { strtUpdateDefaultGroup } from '../app';
import { UPDATE_NODE, addLayer } from '@mapstore/actions/layers';

describe('app epics', function() {
    it('strtUpdateDefaultGroup', function(done) {

        const state = {
            layers: {
                flat: [
                    {
                        id: 'layer01'
                    }
                ],
                groups: [
                    {
                        expanded: true,
                        id: 'Default',
                        name: 'Default',
                        nodes: ['layer01'],
                        title: 'Default'
                    }
                ]
            },
            locale: {
                current: 'it-IT',
                messages: {
                    serapide: {
                        userLayers: 'Livelli Utente'
                    }
                }
            }
        };

        const NUMBER_OF_ACTIONS = 1;

        const callback = (actions) => {
            try {
                const [
                    updateNodeAction
                ] = actions;
                expect(updateNodeAction.type).toBe(UPDATE_NODE);
                expect(updateNodeAction.node).toBe('Default');
                expect(updateNodeAction.nodeType).toBe('groups');
                expect(updateNodeAction.options.title).toBe('Livelli Utente');
            } catch (e) {
                done(e);
            }
            done();
        };

        testEpic(
            strtUpdateDefaultGroup,
            NUMBER_OF_ACTIONS,
            addLayer(),
            callback,
            state);
    });
});
