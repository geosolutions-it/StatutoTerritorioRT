/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import ReactDOM from 'react-dom'
const getEl = (el) => el instanceof Element ? el : document.getElementById(el)

export default class Injector extends React.PureComponent {
    constructor(props) {
        super(props);
        this.el = getEl(props.el);
    }
    render() {
        // Use a portal to render the children into the element
        return this.el ? ReactDOM.createPortal(this.props.children, this.el) :  null;
      }


}