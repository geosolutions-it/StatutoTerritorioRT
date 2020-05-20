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
import { GroupNode } from '../GroupNode';
import { Simulate } from 'react-dom/test-utils';

describe('GroupNode', () => {
    beforeEach((done) => {
        document.body.innerHTML = '<div id="container"></div>';
        setTimeout(done);
    });

    afterEach((done) => {
        ReactDOM.unmountComponentAtNode(document.getElementById("container"));
        document.body.innerHTML = '';
        setTimeout(done);
    });

    it('should be able to replace the whole component', () => {
        const CustomNode = ({ node }) => <div className="custom-node">{node.title}</div>;
        ReactDOM.render(
            <GroupNode
                node={{ title: 'Title' }}
                replaceComponent={() => CustomNode}
            />, document.getElementById("container"));

        const customNode = document.querySelector('.custom-node');
        expect(customNode).toBeTruthy();
        expect(customNode.innerHTML).toBe('Title');
    });

    it('should be able to replace node options without change the state', () => {
        ReactDOM.render(
            <GroupNode
                node={{
                    title: 'ReplaceThisTitle',
                    showComponent: true
                }}
                replaceNodeOptions={(node, nodeType) => ({
                    ...node,
                    ...(nodeType === 'group' && node.title === 'ReplaceThisTitle' && { title: 'New Title' })
                })}
            />, document.getElementById("container"));

        const groupNodeTitle = document.querySelector('.toc-default-group-head .mapstore-side-card-title > span');
        expect(groupNodeTitle).toBeTruthy();
        expect(groupNodeTitle.innerHTML).toBe('New Title');
    });

    it('should select the node', (done) => {
        ReactDOM.render(
            <GroupNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true
                }}
                onSelect={(nodeId, nodeType) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(nodeType).toBe('group');
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const groupNodeHead = document.querySelector('.toc-default-group-head');
        expect(groupNodeHead).toBeTruthy();
        Simulate.click(groupNodeHead);
    });

    it('should select the node', (done) => {
        ReactDOM.render(
            <GroupNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true
                }}
                onSelect={(nodeId, nodeType) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(nodeType).toBe('group');
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const groupNodeHead = document.querySelector('.toc-default-group-head');
        expect(groupNodeHead).toBeTruthy();
        Simulate.click(groupNodeHead);
    });

    it('should trigger on toggle event', (done) => {
        ReactDOM.render(
            <GroupNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true,
                    expanded: false
                }}
                onToggle={(nodeId, expanded) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(expanded).toBe(false);
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const buttons = document.querySelectorAll('.square-button-md');
        expect(buttons.length).toBe(2);
        const expandButton = buttons[0];
        Simulate.click(expandButton);
    });

    it('should trigger change visibility', (done) => {
        ReactDOM.render(
            <GroupNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true,
                    visibility: false
                }}
                propertiesChangeHandler={(nodeId, { visibility }) => {
                    try {
                        expect(nodeId).toBe('node1');
                        expect(visibility).toBe(true);
                    } catch (e) {
                        done(e);
                    }
                    done();
                }}
            />, document.getElementById("container"));

        const buttons = document.querySelectorAll('.square-button-md');
        expect(buttons.length).toBe(2);
        const visibilityButton = buttons[1];
        Simulate.click(visibilityButton);
    });

    it('should add empty class if nodes are empty or undefined', () => {
        ReactDOM.render(
            <GroupNode
                node={{
                    id: 'node1',
                    title: 'Title',
                    showComponent: true,
                    nodes: []
                }}
            />, document.getElementById("container"));

        const emptyNode = document.querySelectorAll('.toc-default-group.ms-empty-group');
        expect(emptyNode).toBeTruthy();
    });

});
