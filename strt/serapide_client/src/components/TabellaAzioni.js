/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Table } from 'reactstrap'

import TextWithTooltip from './TextWithTooltip'


import {formatDate, getActionIcon, getActionIconColor, getAction} from 'utils'
import {rebuildTooltip} from 'enhancers'

const adjustStato = (stato = "", eseguibile) => {
    if(stato.toLowerCase() === "nessuna") {
        return stato.toLowerCase();
    }
    return eseguibile ? "necessaria" : "attesa"
}
const reverseOrder = ({order: a}, {order: b}) => (b - a)

export default rebuildTooltip()(({azioni = [], filtroFase = "anagrafica", className, onExecute = () => {}}) => {
    
    return (
    <Table size="sm" className={className} hover>
        <thead>
            <tr className="size-11">
                <th>Stato</th>
                <th>Azione</th>
                <th>Attori</th>
                <th>Data</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {azioni.filter(({fase = "" }) => fase.toLowerCase() === filtroFase).sort(reverseOrder).map(({stato = "", qualificaRichiesta= "", tipologia = "",label = "", eseguibile = false, tooltip = "", data, uuid} = {}) => {
                let adjustedStato = adjustStato(stato, eseguibile)
                return (<tr key={uuid}>
                            <td><i className={`icon-18 material-icons ${getActionIconColor(adjustedStato)}`}>{getActionIcon(adjustedStato)}</i></td>
                <td>{tooltip ? (<TextWithTooltip className="size-11" dataTip={tooltip} dataTipDisable={!tooltip} text={label}/>) :<span className="size-11">{label}</span>}</td>
                            <td><span className="size-11">{qualificaRichiesta}</span></td>
                            <td className={`${adjustedStato === "attesa" ? "text-serapide" : ""}`}><span className="d-flex size-11">{adjustedStato === "attesa" && <i className="material-icons icon-18 text-serapide" >notifications_activex</i>}<span className="my-auto size-11">{data && formatDate(data)}</span></span></td>
                            <td className={`${adjustedStato !== "nessuna" && eseguibile ? "pointer": ""}`}>{adjustedStato !== "nessuna" && eseguibile && <i className="material-icons text-serapide" onClick={() => onExecute(tipologia, uuid)}>play_circle_filled</i>}</td>
                        </tr>)}
                )}
        </tbody>
    </Table>
)})
