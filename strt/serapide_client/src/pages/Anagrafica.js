/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
// import Button from '../components/IconButton'
import { toast } from 'react-toastify'

import {Query} from "react-apollo"
import {getEnteLabel, getEnteLabelID} from "../utils"
import {GET_PIANI, UPDATE_PIANO} from "../queries"
import {compose, withStateHandlers} from 'recompose'
import {EnhancedDateSelector} from "../components/DateSelector"
import {Input} from 'reactstrap'
import Delibera from '../components/UploadSingleFile'
import UploadFiles from '../components/UploadFiles'
import VAS from '../components/VAS'

const enhancer = compose(withStateHandlers( ({}),
    {
        selectDataDelibera: () => value => ({dataDelibera: value})
    }))
export default enhancer(({match: {params: {code} = {}} = {}, selectDataDelibera, dataDelibera, ...props}) => {

    return (<Query query={GET_PIANI} variables={{codice: code}}>
        {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
            if(loading){
                return (
                    <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    </div>)
            } else if(edges.length === 0) {
                toast.error(`Impossobile trovare il piano: ${code}`,  {autoClose: true})
                return <div></div>
            }
            const {node: {ente, risorse : {edges: resources = []} = {}, tipo = "", codice = ""} = {}} = edges[0] || {}
            
            const {node: delibera} = resources.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            const optionals = resources.filter(({node: n}) => n.tipo === "delibera_liberi").map(({node}) => (node) ) || {};
            const {node: semplificata}= resources.filter(({node: n}) => n.tipo === "vas_semplificata").pop() || {};
            const {node: verifica} = resources.filter(({node: n}) => n.tipo === "vas_verifica").pop() || {};
            return(
            <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                    <div className="d-flex flex-column ">
                        <h4 className="text-uppercase">{getEnteLabel(ente)}</h4>  
                        <div className="pb-4 pt-3 d-flex flex-row">
                            <i className="material-icons text-warning icon-34 pr-4 ">assignment</i>
                            <div className="d-flex flex-column flex-fill">
                                <h3 className="mb-0">CREA ANAGRAFICA</h3>
                                <h3 className="mb-0 text-capitalize">{`${tipo.toLowerCase()} ${codice}`}</h3>
                                <span className="pt-5">{getEnteLabelID(ente)}</span>
                                <div className="d-flex pt-5 align-items-center">
                                    <span className="pr-2">DELIBERA DEL</span>
                                    <EnhancedDateSelector mutation={UPDATE_PIANO} getInput={(val) => ({variables: {input: { pianoOperativo: {dataDelibera: val.toISOString(),  ente: {"code": "FI"}, tipologia: tipo}, codice}}})}/>
                                </div>
                                <div className="d-flex pt-5 align-items-center ">
                                    <span className="pr-2">DESCRIZIONE</span>
                                    <Input type="textarea" name="text" id="deliberText" />
                                </div>
                                <span className="pt-5">DELIBERA COMUNALE</span>
                                <span className="pb-2 font-weight-light">Caricare delibera comunale, formato obbligatorio pdf</span>
                                <Delibera placeholder="Delibera Comunale (obbligatoria)" variables={{codice, tipo: "delibera" }} risorsa={delibera} isLocked={false}/>
                                <span className="pt-5">ALTRI DOCUMENTI</span>
                                <span className="font-weight-light">Caricare eventuali allegati trascinando i files nel riquadro, formato obbligatorio pdf</span>
                                <UploadFiles risorse={optionals} variables={{codice, tipo: "delibera_liberi" }} isLocked={false}/>
                                <div style={{borderBottom: "2px dashed"}} className="mt-5 text-warning" ></div>
                                <VAS codice={codice} semplificata={semplificata} verifica={verifica}></VAS>
                            </div>
                            
                        </div>
                    </div>
                   
            </div>)}
        }
    </Query>)
    })