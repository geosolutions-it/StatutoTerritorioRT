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
import {reverse} from 'lodash'

export default ({azioni = [], className}) => {
    const a = [...azioni]
    return (
    <Table size="sm" className={className} hover>
        <tbody>
            {reverse(a).map(({node: {stato = "", tipologia = "", attore = "", data, uuid}} = {}) => (
                <tr key={uuid}>
                    <td className="text-center"><i className={`material-icons ${getActionIconColor(stato)}`}>{getActionIcon(stato)}</i></td>
                    <td className="text-center text-capitalize">{tipologia.toLowerCase().split("_").join(" ")}</td>
                    <td className="text-center">{attore}</td>
                    <td className="text-center">{stato === "ATTESA" && <i className="material-icons text-warning">notifications_activex\</i>} {data && formatDate(data)}</td>
                    <td className="text-center">{actionHasBtn(attore) && <Button size="sm" color="warning">VAS</Button>}</td>
                    {getAction(stato) &&<td className="text-center" style={{cursor: "pointer"}}><i className="material-icons text-warning">play_circle_filled</i></td>}
                </tr>))}
        </tbody>
    </Table>
)}
