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

import {canExecuteAction} from '../autorizzazioni'
import {formatDate, getActionIcon, getActionIconColor, getAction} from 'utils'
import {rebuildTooltip} from 'enhancers'

const adjustStato = (stato, attore, tipologia) => {
    
    if(stato === "NESSUNA") {
        return stato
    }
    if(canExecuteAction({attore, tipologia})) {
        return "NECESSARIA"
    }
     return "ATTESA"
}
const reverseOrder = ({node: {order: a}}, {node: {order: b}}) => (b - a)

export default rebuildTooltip()(({azioni = [], filtroFase = "anagrafica", className, onExecute = () => {}}) => {
    return (
    <Table size="sm" className={className} hover>
        <thead>
            <tr className="size-8">
                <th>Stato</th>
                <th>Azione</th>
                <th>Attori</th>
                <th>Data</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {azioni.filter(({node: {fase}}) => fase === filtroFase).sort(reverseOrder).map(({node: {stato = "", tipologia = "",label = "", attore = "", tooltip = "", data, uuid}} = {}) => {
                let adjustedStato = adjustStato(stato, attore, tipologia)
                return (<tr key={uuid}>
                            <td><i className={`icon-18 material-icons ${getActionIconColor(adjustedStato)}`}>{getActionIcon(adjustedStato)}</i></td>
                <td>{tooltip ? (<TextWithTooltip className="size-11" dataTip={tooltip} dataTipDisable={!tooltip} text={label}/>) :<span className="size-11">{label}</span>}</td>
                            <td><span className="size-11">{attore}</span></td>
                            <td className={`${adjustedStato === "ATTESA" ? "text-serapide" : ""}`}><span className="d-flex size-11">{adjustedStato === "ATTESA" && <i className="material-icons text-serapide" style={{width: 28}}>notifications_activex</i>}<span className="my-auto size-11">{data && formatDate(data)}</span></span></td>
                            <td className={`${getAction(adjustedStato) && canExecuteAction({attore, tipologia})  ? "pointer": ""}`}>{getAction(adjustedStato) && canExecuteAction({attore, tipologia}) && <i className="material-icons text-serapide" onClick={() => onExecute(tipologia, uuid)}>play_circle_filled</i>}</td>
                        </tr>)}
                )}
        </tbody>
    </Table>
)})
