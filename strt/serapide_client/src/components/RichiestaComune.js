/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import  {formatDate} from 'utils'

export default ({scadenza, formato = "dd MMMM yyyy", label = "Richiesta Comune", icon = "check_circle_outline", className = "row d-flex mb-3 mt-3"} ) => (
    <div className={className}>
    <div className="col-6 d-flex">
        <i className="material-icons text-serapide">{icon}</i>
        <span className="pl-2">{label}</span>
    </div>
    <div className="col-6">{scadenza && formatDate(scadenza, formato)}</div>
</div>
)