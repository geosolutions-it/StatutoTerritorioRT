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
const getActive = (stato, currentStato  = "" ) => stato === currentStato.toLowerCase() ? "active" : ''

export default ({stato: {nome = "Unknown", codice, descrizione}}) => {
    const id =  `_${shortid.generate()}`
    return (
        <span className="stato-progress">
            <i id={id} className={`material-icons ${nome.toLowerCase()}`}>room</i>
            <ul className={`_${nome.toLowerCase()}`}>
                <li></li>
                <li id="_avvio" className={getActive("avvio", nome)}></li>
                <li id="_adozione" className={getActive("adozione", nome)}></li>
                <li id="_approvazione" className={getActive("approvazione", nome)}></li>
                <li id="_pubblicazione" className={getActive("pubblicazione", nome)}></li>
                <UncontrolledTooltip placement="top" target={id} ><span className="text-capitalize">{nome.toLowerCase()}</span></UncontrolledTooltip>
            </ul>
        </span>)
    }