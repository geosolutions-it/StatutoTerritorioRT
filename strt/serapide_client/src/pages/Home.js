/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Azioni from '../components/TabellaAzioni'

export default ({azioni = []}) => (
    <div className="d-flex flex-column pb-4 pt-5">
        <div className="d-flex border-warning border-top border-bottom py-4 justify-content-around">
            <span>LEGGENDA</span>
            <span className="d-flex"><i className="material-icons text-warning mr-2">alarm_add</i><span>E’ richiesta un’azione</span></span>
            <span className="d-flex"><i className="material-icons text-warning mr-2">alarm_on</i><span>In attesa di risposta da altri attori</span></span>
            <span className="d-flex"><i className="material-icons text-warning mr-2">alarm_off</i><span>Nessuna azione richiesta</span></span>
        </div>
        <div className="py-4">
            <Azioni azioni={azioni}/>
        </div>
    </div>
)