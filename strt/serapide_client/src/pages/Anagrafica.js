/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
// import Button from '../components/IconButton'
import gql from "graphql-tag";
import { Mutation } from "react-apollo";
import {get} from "lodash";

const NUOVO_PIANO= gql`
mutation NuovoPiano($t: Tipi!){
	nuovoPiano(tipo: $t){
    code,
    tipo    
  }
}
`;
export default (props) => {
    return (
        <Mutation mutation={NUOVO_PIANO} onCompleted={() => window.location.href="#/anagrafica"}>
            {(creaPiano, { loading, error }) => (
            <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                    <div className="d-flex flex-column ">
                        <h4 className="text-uppercase">{get(props, "user.organizzazione", "")}</h4>  
                        <div className="pb-4 pt-3 d-flex flex-row">
                            <i className="material-icons text-warning icon-34 pr-4 ">assignment</i>
                            <div className="d-flex flex-column ">
                                <h3 className="mb-0">CREA ANAGRAFICA</h3>
                                <h3 className="mb-0">{`${get(props, "piano.tipo", "")} ${get(props, "piano.code", "")}`}</h3>
                                <span className="pt-5">ID COMUNE B962</span>
                                <div className="d-flex"><span className="pt-5">DELIBERA DEL</span></div>
                            </div>   
                        </div>
                    </div>
            </div>)}
        </Mutation>)
    }