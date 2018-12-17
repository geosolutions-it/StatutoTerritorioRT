/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import ReactDOM from 'react-dom'

export default class NavBar extends React.PureComponent {
    constructor(props) {
        super(props);
        this.pBar = document.getElementById('inject');
    }
    render() {
        // Use a portal to render the children into the element
        return ReactDOM.createPortal(
          // Any valid React child: JSX, strings, arrays, etc.
          this.props.children,
          // A DOM element
          this.pBar
        )
      }


}