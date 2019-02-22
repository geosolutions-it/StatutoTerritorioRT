/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
export default class Injector extends React.PureComponent {
    constructor(props) {
        super(props)
        this.el = document.body
    }
    componentDidMount() {
        if(this.props.themeClass) {
            this.inject(this.props.themeClass)
        }
    } 
    componentDidUpdate() {
        if(this.props.themeClass) {
            this.inject(this.props.themeClass)
        }
    }
    componentWillUnmount() {
        this.el = null
    }
    inject  = (c) => {
        if (! document.body.classList.contains(c) ) {
            this.el.classList.add(c)
        }
    }
    render() {
        return null
      }


}