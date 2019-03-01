/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import shortid from "shortid"
import {fasi} from "../utils"
import classNames from "classnames"

export default ({stato: {nome = "Unknown", codice}, className= "stato-progress", legend= false}) => {
    const id =  `_${shortid.generate()}`
    const activeIdx = fasi.indexOf(nome.toLocaleLowerCase()) + 1
    const activeFase = fasi[activeIdx]
    const toolTip = { "data-tip": `<span class="text-capitalize">${activeFase.toLowerCase()}</span>`, "data-html": true}
    return (
        <span className={className}>
            <i id={id} {...toolTip} className={`material-icons text-serapide ${activeFase}`}>room</i>
            <ul className={`_icons _${activeFase}`}>
                {fasi.map((fase, idx) => (<li key={`_${fase}`} id={`_${fase}`} className={classNames({"bg-serapide": activeIdx >= idx})}/>))}
            </ul>
            {legend && (
                <React.Fragment>
                 <ul className={`_${activeFase} _labels`}>
                    {fasi.map((fase, idx) => (<li key={`label_${fase}`} id={`label_${fase}`} className={classNames(`label_${fase}`, fase)}>{fase}</li>))}
                 </ul>    
                </React.Fragment>)}
        </span>)
    }