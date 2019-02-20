/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { UncontrolledTooltip } from 'reactstrap'
import shortid from "shortid"
import {fasi} from "../utils"
import classNames from "classnames"

export default ({stato: {nome = "Unknown", codice}, className= "stato-progress", legend= false}) => {
    const id =  `_${shortid.generate()}`
    const activeFase = fasi[fasi.indexOf(nome.toLocaleLowerCase()) + 1]
    return (
        <span className={className}>
            <i id={id} className={`material-icons ${activeFase}`}>room</i>
            <ul className={`_${activeFase} _icons`}>
                {fasi.map((fase, idx) => (<li key={`_${fase}`} id={`_${fase}`} className={classNames({active: activeFase === fase})}/>))}
                {!legend && <UncontrolledTooltip placement="top" target={id} ><span className="text-capitalize">{nome.toLowerCase()}</span></UncontrolledTooltip>}
            </ul>
            {legend && (
                <React.Fragment>
                 <ul className={`_${activeFase} _labels`}>
                    {fasi.map((fase, idx) => (<li key={`label_${fase}`} id={`label_${fase}`} className={classNames(`label_${fase}`, fase)}>{fase}</li>))}
                 </ul>    
                </React.Fragment>)}
        </span>)
    }