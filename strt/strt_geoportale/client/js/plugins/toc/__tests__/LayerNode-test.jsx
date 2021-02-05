/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import expect from 'expect';
import { LayerNode } from '../LayerNode';
import { Simulate } from 'react-dom/test-utils';

describe('LayerNode', () => {
    beforeEach((done) => {
        document.body.innerHTML = '<div id="container"></div>';
        setTimeout(done);
    });

    afterEach((done) => {
        ReactDOM.unmountComponentAtNode(document.getElementById("container"));
        document.body.innerHTML = '';
        setTimeout(done);
    });

    it('should be able to replace node options without change the state', () => {
        ReactDOM.render(
            <LayerNode
                node={{
                    title: 'ReplaceThisTitle',
                    showComponent: true
                }}
                replaceNodeOptions={(node, nodeType) => ({
                    ...node,
                    ...(nodeType === 'layer' && node.title === 'ReplaceThisTitle' && { title: 'New Title' })
                })}
            />, document.getElementById("container"));

        const layerNodeTitle = document.querySelector('.ms-toc-layer .mapstore-side-card-title > span');
        expect(layerNodeTitle).toBeTruthy();
        expect(layerNodeTitle.innerHTML).toBe('New Title');
    });

    it('should select the node', (done) => {
        ReactDOM.render(
            <LayerNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true
                }}
                onSelect={(nodeId, nodeType) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(nodeType).toBe('layer');
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const layerNodeHead = document.querySelector('.ms-toc-layer');
        expect(layerNodeHead).toBeTruthy();
        Simulate.click(layerNodeHead);
    });

    it('should trigger change visibility', (done) => {
        ReactDOM.render(
            <LayerNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true,
                    visibility: false
                }}
                onUpdateNode={(nodeId, nodeType, { visibility }) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(nodeType).toBe('layer');
                        expect(visibility).toBe(true);
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const buttons = document.querySelectorAll('.square-button-md .glyphicon');
        expect(buttons.length).toBe(2);
        const visibilityButton = buttons[1];
        Simulate.click(visibilityButton);
    });

});
