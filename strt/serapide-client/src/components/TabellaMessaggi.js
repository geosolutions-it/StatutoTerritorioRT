/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Table } from 'reactstrap'

export default ({title, messaggi = []}) => (
        <Table className="pb-4" size="sm" hover>
            <tbody>
                {messaggi.map(({ id, data, from, testo}) => (
                    <tr key={id}>
                        <td className="text-center"><i className="material-icons text-warning">fiber_manual_record</i></td>
                        <td className="text-center">{data}</td>
                        <td className="text-center">
                            <span className="d-inline-flex flex-column">
                                <span className="text-nowrap">{from.nome}</span>
                                <span className="text-nowrap text-uppercase">{from.organizzazione}</span>
                            </span>
                        </td>
                        <td>{testo}</td>
                    </tr>))}
                </tbody>
            </Table>
)
