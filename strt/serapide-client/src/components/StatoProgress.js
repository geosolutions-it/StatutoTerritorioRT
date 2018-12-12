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
const getActive = (stato, currentStato) => stato === currentStato ? "active" : ''


export default ({stato = "avvio"}) => {
    const id =  `_${shortid.generate()}`
    return (
        <span className="stato-progress">
            <i id={id} className={`material-icons text-warning ${stato}`}>room</i>
            <ul>
                <li></li>
                <li id="_avvio" className={getActive("avvio", stato)}></li>
                <li id="_adozione" className={getActive("adozione", stato)}></li>
                <li id="_approvazione" className={getActive("approvazione", stato)}></li>
                <li id="_pubblicazione" className={getActive("pubblicazione", stato)}></li>
                <UncontrolledTooltip placement="top" target={id} ><span className="text-capitalize">{stato}</span></UncontrolledTooltip>
            </ul>
        </span>)
    }