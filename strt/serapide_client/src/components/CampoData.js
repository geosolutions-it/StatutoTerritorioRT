/*
 * Copyright 2020, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {formatDate, getDate} from 'utils'

/**
 * Se azione non è chiusa ed ha una scadenza viene mostrata sveglia gialla, se la scadenza è passata sveglia rossa
 */
export default ({chiusura, scadenza}) => {
    const isClosed = !!chiusura;
    const hasScadenza = !isClosed && !!scadenza
    const isExpired = hasScadenza && !isClosed && (getDate(scadenza) < getDate(new Date()))
    let color = ""
    if(isExpired) {
        color = "text-danger"
    }else if(hasScadenza){
        color = "text-serapide"
    }
    const data = chiusura || scadenza
    return (<td className={color}><span className="d-flex size-11">{hasScadenza && <i className={`material-icons icon-18 ${color}`}>notifications_active</i>}<span className={`my-auto size-11 ${hasScadenza && "ml-1"} ${color}`}>{data && formatDate(data)}</span></span></td>)
}