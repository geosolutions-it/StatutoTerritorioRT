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
import {Button} from 'reactstrap'
const reverseOrder = ({node: {order: a}}, {node: {order: b}}) => (b - a)

export default ({azioni = [], className}) => {
    return (
    <Table size="sm" className={className} hover>
        <tbody>
            {azioni.sort(reverseOrder).map(({node: {stato = "", tipologia = "", attore = "", data, uuid}} = {}) => (
                <tr key={uuid}>
                    <td className="text-center"><i className={`material-icons ${getActionIconColor(stato)}`}>{getActionIcon(stato)}</i></td>
                    <td className="text-center text-capitalize">{tipologia.toLowerCase().split("_").join(" ")}</td>
                    <td className="text-center">{attore}</td>
                    <td className={`text-center ${stato === "ATTESA" ? "text-warning" : ""}`}><span className="d-flex justify-content-center">{stato === "ATTESA" && <i className="material-icons text-warning" style={{width: 28}}>notifications_activex</i>} {data && formatDate(data)}</span></td>
                    <td className="text-center">{actionHasBtn(attore) && <Button size="sm" color="warning">VAS</Button>}</td>
                    <td className={`text-center ${getAction(stato) ? "pointer": ""}`}>{getAction(stato) && <i className="material-icons text-warning">play_circle_filled</i>}</td>
                </tr>))}
        </tbody>
    </Table>
)}
