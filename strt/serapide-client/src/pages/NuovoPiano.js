/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Button from '../components/IconButton'
import {defaultProps} from 'recompose'
import {user, messaggi}  from '../resources'
import SelectTipo from '../components/SelectTipo'
export default defaultProps({user, messaggi})((props) => {
    return (
        <React.Fragment>
            <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                    <div className="d-flex flex-column ">
                        <h4 className="text-uppercase">{user.organizzazione}</h4>  
                        <div className="pb-4 pt-3 d-flex flex-row">
                            <i className="material-icons text-warning icon-34 pr-4 ">assignment</i>
                            <div className="d-flex flex-column ">
                                <h3 className="mb-0">CREA NUOVO PIANO</h3>
                                <span className="pt-5">ID COMUNE B962</span>
                                <span className="pt-4 pb-2 font-weight-bold">Atto di governo del territorio</span>
                                <span className="pt-2 pb-1small">Seleziona il tipo di atto</span>
                                <SelectTipo></SelectTipo>
                                <Button size='md' tag="a" href="./#/nuovo_piano" className="mt-5 flex-column d-flex ext-uppercase align-items-center" color="warning" label="CREA PIANO"></Button>
                            </div>   
                        </div>
                    </div>
            </div>
        </React.Fragment>)
    })