/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Table } from 'reactstrap'
import {formatDate, getActionIcon, getActionIconColor, getAction, actionHasBtn} from '../utils'
import {canExecuteAction} from '../autorizzazioni'
import {Button} from 'reactstrap'
const reverseOrder = ({node: {order: a}}, {node: {order: b}}) => (b - a)
export default ({azioni = [], className, onExecute = () => {}}) => {
    return (
    <Table size="sm" className={className} hover>
        <thead>
            <tr>
                <th>Stato</th>
                <th>Azione</th>
                <th>Attori</th>
                <th>Data</th>
                <th></th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {azioni.sort(reverseOrder).map(({node: {stato = "", tipologia = "", attore = "", data, uuid}} = {}) => (
                <tr key={uuid}>
                    <td><i className={`material-icons ${getActionIconColor(stato)}`}>{getActionIcon(stato)}</i></td>
                    <td className="text-capitalize">{tipologia.toLowerCase().split("_").join(" ")}</td>
                    <td>{attore}</td>
                    <td className={`${stato === "ATTESA" ? "text-serapide" : ""}`}><span className="d-flex">{stato === "ATTESA" && <i className="material-icons text-serapide" style={{width: 28}}>notifications_activex</i>} {data && formatDate(data)}</span></td>
                    <td>{actionHasBtn(attore) && <Button size="sm" color="serapide">VAS</Button>}</td>
                    <td className={`${getAction(stato) && canExecuteAction({attore, tipologia})  ? "pointer": ""}`}>{getAction(stato) && canExecuteAction({attore, tipologia}) && <i className="material-icons text-serapide" onClick={() => onExecute(tipologia)}>play_circle_filled</i>}</td>
                </tr>))}
        </tbody>
    </Table>
)}
