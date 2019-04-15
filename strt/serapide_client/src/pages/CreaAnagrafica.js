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
import {getEnteLabel, getEnteLabelID} from "../utils"
import {GET_PIANI, UPDATE_PIANO} from "../graphql"

import {EnhancedDateSelector} from "../components/DateSelector"

import Delibera from '../components/UploadSingleFile'
import UploadFiles from '../components/UploadFiles'
import VAS from '../components/VAS'
import EnhanchedInput from '../components/EnhancedInput'

const getPianoLabel = (tipo) => tipo === "variante" ? `${tipo} piano` : `piano ${tipo}`

const getDescrizioneInput = (codice) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: {
            descrizione: val}, 
        codice}
    }})

const getDataDeliberaInput = (codice) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: {
            dataDelibera: val.toISOString()}, 
        codice}
    }})

const canCommit = (dataDelibera, delibera, descrizione = "") =>  dataDelibera && delibera && descrizione


export default ({match: {params: {code} = {}} = {}, selectDataDelibera, dataDelibera, ...props}) => {
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
            const {node: {ente, fase: {nome: faseNome}, risorse : {edges: resources = []} = {}, tipo = "", codice = "", dataDelibera, descrizione} = {}} = edges[0] || {}
            const locked = faseNome !== "DRAFT"
            const {node: delibera} = resources.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            const optionals = resources.filter(({node: n}) => n.tipo === "delibera_opts").map(({node}) => (node) ) || {};
            if(locked) {
                window.location.href=`#/pino/${code}/anagrafica`
            }
            return(
            <div>
                    <div className="d-flex flex-column ">
                        <h4 className="text-uppercase">{getEnteLabel(ente)}</h4>  
                        <div className="pb-4 pt-3 d-flex flex-row">
                            <i className="material-icons text-serapide icon-34 pr-4 ">assignment</i>
                            <div className="d-flex flex-column flex-fill">
                                <h3 className="mb-0">CREA ANAGRAFICA</h3>
                                <h3 className="mb-0 text-capitalize">{`${getPianoLabel(tipo.toLowerCase())} ${codice}`}</h3>
                                <span className="pt-5">{getEnteLabelID(ente)}</span>
                                <h5 className="pt-5 pb-2">Delibera di Consiglio/Giunta</h5>
                                <div className="row d-flex align-items-center">
                                    <span className="col-4 ">DELIBERA DEL</span>
                                    <div className="col-8 "><EnhancedDateSelector disabled={locked} selected={dataDelibera ? new Date(dataDelibera) : undefined} mutation={UPDATE_PIANO} getInput={getDataDeliberaInput(codice)}/></div>
                                </div>
                                <div className="row d-flex pt-5 align-items-center ">
                                    <span className="col-4">DENOMINAZIONE DELL’ATTO</span>
                                    <div className="col-8 "><EnhanchedInput disabled={locked} value={descrizione} mutation={UPDATE_PIANO} getInput={getDescrizioneInput(codice)}></EnhanchedInput></div>
                                    
                                </div>
                                <span className="pt-5">DELIBERA DI AVVIO DEL PROCEDIMENTO</span>
                                <span className="pb-2 font-weight-light">Caricare delibera, formato obbligatorio pdf</span>
                                <Delibera placeholder="Delibera (obbligatoria)" variables={{codice, tipo: "delibera" }} risorsa={delibera} isLocked={locked}/>
                                <span className="pt-5">ALTRI DOCUMENTI</span>
                                <span className="font-weight-light">Caricare eventuali allegati trascinando i files nel riquadro, formato obbligatorio pdf</span>
                                <UploadFiles risorse={optionals} variables={{codice, tipo: "delibera_opts" }} isLocked={locked}/>
                                <div style={{borderBottom: "2px dashed"}} className="mt-5 text-serapide" ></div>
                                <VAS codice={codice} canUpdate={canCommit(dataDelibera, delibera, descrizione)} isLocked={locked}></VAS>
                            </div>
                            
                        </div>
                    </div>
                   
            </div>)}
        }
    </Query>)
    }