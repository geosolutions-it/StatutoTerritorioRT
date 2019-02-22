/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import { toast } from 'react-toastify'

import {Query} from "react-apollo"
import {getEnteLabelID} from "../utils"
import {GET_PIANI, UPDATE_PIANO} from "../queries"

import {EnhancedDateSelector} from "../components/DateSelector"

import Delibera from '../components/UploadSingleFile'
import UploadFiles from '../components/UploadFiles'
import VAS from '../components/VAS'


const getDataDeliberaInput = (codice) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: {
            dataDelibera: val.toISOString()}, 
        codice}
    }})

const canCommit = (dataDelibera, delibera, descrizione = "") =>  dataDelibera && delibera && descrizione && descrizione.length > 0


export default ({match: {params: {code} = {}} = {}, ...props}) => {
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
            const {node: {ente, fase: {nome: faseNome}, risorse : {edges: resources = []} = {}, codice = "", dataDelibera, descrizione} = {}} = edges[0] || {}
            const locked = faseNome !== "DRAFT"
            const {node: delibera} = resources.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            const optionals = resources.filter(({node: n}) => n.tipo === "delibera_opts").map(({node}) => (node) ) || {};
            if(!locked) {
                window.location.href=`#/crea_anagrafica/${code}`
            }
            return(
                        <div className="pb-4 pt-5 d-flex flex-row">
                            <i className="material-icons text-serapide icon-34">assignment</i>
                            <i style={{maxWidth: 26}} className="material-icons text-serapide">locked</i>
                            <div className="d-flex flex-column flex-fill">
                                <h3 className="mb-0">ANAGRAFICA</h3>
                                <span className="pt-5">{getEnteLabelID(ente)}</span>
                                <div className="d-flex pt-5 align-items-center">
                                    <span className="pr-2">DELIBERA DEL</span>
                                    <EnhancedDateSelector isLocked={locked} selected={dataDelibera ? new Date(dataDelibera) : undefined} mutation={UPDATE_PIANO} getInput={getDataDeliberaInput(codice)}/>
                                </div>
                                <span className="pt-5">DELIBERA COMUNALE</span>
                                <Delibera placeholder="Delibera Comunale (obbligatoria)" variables={{codice, tipo: "delibera" }} risorsa={delibera} isLocked={locked}/>
                                <span className="pt-5">ALTRI DOCUMENTI</span>
                                <UploadFiles risorse={optionals} variables={{codice, tipo: "delibera_opts" }} isLocked={locked}/>
                                <div style={{borderBottom: "2px dashed"}} className="mt-5 text-serapide" ></div>
                                <VAS codice={codice} canUpdate={canCommit(dataDelibera, delibera, descrizione)} isLocked={locked}></VAS>
                            </div>
                            
                        </div>
                   
            )}
        }
    </Query>)
    }