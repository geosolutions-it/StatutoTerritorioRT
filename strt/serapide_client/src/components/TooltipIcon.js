/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

export default ({dataTip, dataTipDisable, text = ""}) => {
    return text ?
    (<span className="text-nowrap">{text}<i data-tip={dataTip} data-tip-disable={dataTipDisable} className="material-icons text-serapide align-top icon-12">info</i></span>) : 
    (<i data-tip={dataTip} data-tip-disable={dataTipDisable} className="material-icons text-serapide align-top icon-12">info</i>)
}