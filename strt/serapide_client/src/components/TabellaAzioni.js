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


const canExecute = (stato, eseguibile) => (stato === "NECESSARIA" || stato === "ATTESA") && eseguibile
const reverseOrder = ({order: a}, {order: b}) => (b - a)
const adjustStato = (stato = "", lottoErrato) => {
    return !!lottoErrato && (stato === "NECESSARIA" || stato === "ATTESA") ? "FALLITA" : stato;
}
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
            {azioni.filter(({fase = "" , qualificaRichiesta = ""}) => (fase ?? "").toLowerCase() === filtroFase && qualificaRichiesta !== "AUTO").sort(reverseOrder).map(({stato = "", qualificaRichiesta= "", tipologia = "",label = "", eseguibile = false, tooltip = "", data: dataChiusura, scadenza, uuid, lottoErrato} = {}) => {
                return (<tr key={uuid}>
                            <td><i className={`icon-18 material-icons ${getActionIconColor(adjustStato(stato, lottoErrato))}`}>{getActionIcon(adjustStato(stato, lottoErrato))}</i></td>
                <td>{tooltip ? (<TextWithTooltip className="size-11" dataTip={tooltip} dataTipDisable={!tooltip} text={label}/>) :<span className="size-11">{label}</span>}</td>
                            <td><span className="size-11">{qualificaRichiesta}</span></td>
                            <CampoData chiusura={dataChiusura} scadenza={scadenza}></CampoData>
                            <td className={`${canExecute(stato, eseguibile)? "pointer": ""}`}>{canExecute(stato, eseguibile) && <i className={`material-icons ${getActionIconColor(adjustStato(stato, lottoErrato))}`} onClick={() => onExecute(tipologia, uuid)}>play_circle_filled</i>}</td>
                        </tr>)}
                )}
        </tbody>
    </Table>
)})
