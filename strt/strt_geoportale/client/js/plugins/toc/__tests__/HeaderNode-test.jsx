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
import HeaderNode from '../HeaderNode';

describe('HeaderNode', () => {
    beforeEach((done) => {
        document.body.innerHTML = '<div id="container"></div>';
        setTimeout(done);
    });

    afterEach((done) => {
        ReactDOM.unmountComponentAtNode(document.getElementById("container"));
        document.body.innerHTML = '';
        setTimeout(done);
    });

    it('should render title and filter input', () => {
        ReactDOM.render(<HeaderNode
            node={{
                title: 'Title'
            }}
        />, document.getElementById("container"));
        const headerNode = document.querySelector('.ms-header-node');
        expect(headerNode).toBeTruthy();
        const filterNode = headerNode.querySelector('.mapstore-filter');
        expect(filterNode).toBeTruthy();

        const titleNode = headerNode.querySelector('.ms-header-node-title > div:first-child');
        expect(titleNode).toBeTruthy();
        expect(titleNode.innerHTML).toBe('Title');
    });
});
