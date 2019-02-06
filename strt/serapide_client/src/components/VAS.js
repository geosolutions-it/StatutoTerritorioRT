/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Switch, {EnhancedSwitch} from './Switch'
import FileUpload from './UploadSingleFile'
import Button from './IconButton'

import {EnhancedListSelector} from './ListSelector'
import {GET_VAS_AUTHORITIES, GET_VAS, VAS_FILE_UPLOAD, DELETE_RISORSA_VAS, UPDATE_VAS} from '../queries'
import { Query } from 'react-apollo';
const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success
const getVasTypeInput = (uuid) => (tipologia) => ({
    variables: {
        input: { 
            proceduraVas: {
            tipologia}, 
        uuid}
    }
})
export default ({codice}) => {
    return (
        <Query query={GET_VAS} variables={{codice}}>
            {({loading, data: {procedureVas: {edges = []} = []} = {}}) => {
                if(loading){
                    return (
                    <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    </div>)
            }
            
            const {node: {uuid, tipologia, piano: {codice} = {}, risorse : {edges: resources = []} = {}} = {}} = edges[0] || {}
            console.log(uuid, edges)
            const {node: semplificata}= resources.filter(({node: n}) => n.tipo === "vas_semplificata").pop() || {};
            const {node: verifica} = resources.filter(({node: n}) => n.tipo === "vas_verifica").pop() || {};
            const disableSCA = tipologia === "SEMPLIFICATA" || tipologia === "NON_NECESSARIA"
            return(
            <React.Fragment>
                <span className="pt-4">PROCEDIMENTO VAS</span>
                <span className="pt-2">NOTA : Le opzioni sono escludenti. Se viene selezionata la richiesta della VAS semplificata
                    è richiesto l’upload della Relazione Motivata; se viene selezionata la Richiesta di Verifica VAS è richiesto
                    l’upload del documento preliminare di verifica; se si seleziona il Procedimento Vas si decide di seguire il procedimento VAS esteso.</span>
                <EnhancedSwitch  getInput={getVasTypeInput(uuid)} mutation={UPDATE_VAS} value="semplificata" checked={tipologia === "SEMPLIFICATA"}  label="RICHIESTA VAS SEMPLIFICATA" className="mt-3 vas-EnhancedSwitch justify-content-between">
                    {(checked) =>
                        <FileUpload getSuccess={getSuccess}  mutation={VAS_FILE_UPLOAD} resourceMutation={DELETE_RISORSA_VAS} disabled={!checked} isLocked={!checked} risorsa={semplificata} placeholder="Relazione motivata per VAS semplificata" variables={{codice: uuid, tipo: "vas_semplificata" }}/>
                    }
                </EnhancedSwitch>
                <EnhancedSwitch  getInput={getVasTypeInput(uuid)}  mutation={UPDATE_VAS} value="verifica" checked={tipologia === "VERIFICA"}  label="RICHIESTA VERIFICA VAS" className=" justify-content-between vas-EnhancedSwitch mb-2">
                    {(checked) => <FileUpload getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} resourceMutation={DELETE_RISORSA_VAS} disabled={!checked} isLocked={!checked} risorsa={verifica} placeholder="Documento preliminare di verifica" variables={{codice: uuid, tipo: "vas_verifica" }}/>}
                </EnhancedSwitch>
                <EnhancedSwitch getInput={getVasTypeInput(uuid)}  mutation={UPDATE_VAS} value="procedimento" checked={tipologia === "PROCEDIMENTO"}  label="PROCEDIMENTO VAS (AVVIO)" className=" justify-content-between vas-EnhancedSwitch mb-2">
                    {() => (
                        <span className="p-3">Scegliendo “Procedura VAS” verrà inviata una comunicazione all’autorità procedente e proponente (AP/P)
                    che avvierà le consultazioni degli Soggetti Competenti in Materia Ambientale (SCA)</span>
                        
                    )}
                </EnhancedSwitch>
                <EnhancedSwitch  getInput={getVasTypeInput(uuid)} mutation={UPDATE_VAS} value="non_necessaria"  checked={tipologia === "NON_NECESSARIA"}  label="VAS NON NECESSARIA" className=" justify-content-between vas-EnhancedSwitch">
                        {() =>(<span className="p-3">In questo caso per il piano non è necessaria alcuna VAS </span>)}
                </EnhancedSwitch>
                <div className="d-flex justify-content-between mb-3">
                    <div style={{minWidth: "50%"}}>
                        <EnhancedListSelector
                                query={GET_VAS_AUTHORITIES}
                                label="SELEZIONA AUTORITA’ COMPETENTE VAS"
                                btn={(toggleOpen) => (<Button onClick={toggleOpen} className="text-uppercase" color="warning" icon="add_circle" label="IDENTIFICA L’AUTORITA’ COMPETENTE VAS (AC)"/>)}
                            ></EnhancedListSelector>
                    </div>
                    <div style={{minWidth: "50%"}}>
                    <EnhancedListSelector
                                query={GET_VAS_AUTHORITIES}
                                label="SELEZIONA AUTORITA’ COMPETENTE VAS"
                                btn={(toggleOpen) => (<Button className="my-auto text-uppercase" disabled={disableSCA} color="warning" icon="add_circle" label="IDENTIFICA SOGGETTI COMPETENTI IN MATERIA AMBIENTALE (SCA)"></Button>)}
                            ></EnhancedListSelector>
                    </div>
                </div>
            </React.Fragment>)}}
         </Query>)
        }