/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Table } from 'reactstrap'
import {formatDate} from 'utils'
export default ({title, messaggi = []}) => (
        <Table className="pb-4" size="sm" hover>
            <tbody>
                {messaggi.map(({sentAt, content, thread: {id, absoluteUrl, subject} = {}, sender: {email, firstName, lastName} = {}}) => (
                    <tr key={id} onClick={() => window.location.href = absoluteUrl} className="pointer">
                        <td className="text-center"><i className="material-icons text-serapide">fiber_manual_record</i></td>
                        <td className="text-center">{formatDate(sentAt)}</td>
                        <td className="text-center">
                            <span className="d-inline-flex flex-column">
                                <span className="text-nowrap">{`${firstName} ${lastName}`}</span>
                                <span className="text-nowrap text-uppercase">{email}</span>
                            </span>
                        </td>
                        <td>{subject}</td>
                    </tr>))}
                    {messaggi.length === 0 && (<tr><td>Nessun messaggio da leggere</td></tr>)}
                </tbody>
            </Table>
)
