/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import  {formatDate} from 'utils'

export default ({scadenza, iconSize = '', fontSize = '', formato = "dd MMMM yyyy", label = "Richiesta Comune", icon = "check_circle_outline", className = "row d-flex mb-3 mt-3"} ) => (
    <div className={className}>
    <div className="col-6 d-flex align-item-center">
        <i className= {`material-icons text-serapide ${iconSize}`}>{icon}</i>
        <span className={`pl-2 ${fontSize}`}>{label}</span>
    </div>
    <div className={`col-6 ${fontSize}`}>{scadenza && formatDate(scadenza, formato)}</div>
</div>
)