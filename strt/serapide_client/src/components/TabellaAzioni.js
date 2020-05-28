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
import CampoData from './CampoData'

import {getActionIcon, getActionIconColor, getDate} from 'utils'
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
            {azioni.filter(({fase = "" }) => (fase ?? "").toLowerCase() === filtroFase).sort(reverseOrder).map(({stato = "", qualificaRichiesta= "", tipologia = "",label = "", eseguibile = false, tooltip = "", data: dataChiusura, scadenza, uuid} = {}) => {
                let disabled = false;
                if(tipologia === "osservazioni_enti" && (getDate(scadenza) < getDate(new Date()))) {
                    disabled = true
                }
                let adjustedStato = adjustStato(stato, eseguibile)
                return (<tr key={uuid}>
                            <td><i className={`icon-18 material-icons ${getActionIconColor(adjustedStato.toUpperCase())}`}>{getActionIcon(adjustedStato.toUpperCase())}</i></td>
                <td>{tooltip ? (<TextWithTooltip className="size-11" dataTip={tooltip} dataTipDisable={!tooltip} text={label}/>) :<span className="size-11">{label}</span>}</td>
                            <td><span className="size-11">{qualificaRichiesta}</span></td>
                            <CampoData chiusura={dataChiusura} scadenza={scadenza}></CampoData>
                            <td className={`${adjustedStato !== "nessuna" && eseguibile && !disabled ? "pointer": ""}`}>{adjustedStato !== "nessuna" && eseguibile && !disabled && <i className="material-icons text-serapide" onClick={() => onExecute(tipologia, uuid)}>play_circle_filled</i>}</td>
                        </tr>)}
                )}
        </tbody>
    </Table>
)})
