/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import Resource from '../../components/Resource'
import {Query, Mutation} from 'react-apollo'
import {GET_CONSULTAZIONE_VAS,
    DELETE_RISORSA_CONSULTAZIONE_VAS,
    CONSULTAZIONE_VAS_FILE_UPLOAD
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import  {showError, formatDate} from '../../utils'

const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({consultazioneSCA: {node: { dataCreazione, dataRicezionePareri, dataScadenza, risorse: {edges=[]} = {}, uuid} = {}} = {}, utente: {fiscalCode} = {}}) => {
    const docPrelim = (edges.filter(({node: {tipo}}) => tipo === "consultazione_vas_preliminare").pop() || {}).node
    const docParere = (edges.filter(({node: {tipo, user = {}}}) => tipo === "consultazione_vas_parere" && fiscalCode === user.fiscalCode).pop() || {}).node
    return (
        <React.Fragment>
            <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Pareri SCA</h2></div>
            <div className="d-flex mb-3 mt-3 justify-content-between">
                <div className="d-flex">
                    <i className="material-icons text-serapide">check_circle_outline</i>
                    <span className="pl-2">Richiesta Comune</span>
                </div>
                <div>{formatDate(dataCreazione, "dd MMMM yyyy")}</div>
            </div>
            <Resource className="border-0 mt-2" icon="attach_file" resource={docPrelim}></Resource>
            <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                    <i className="material-icons text-serapide pr-3">event_busy</i> 
                    <div className="d-flex flex-column">
                        <span>{formatDate(dataScadenza, "dd MMMM yyyy")}</span>
                        <span>Data entro la quale ricevere i pareri</span>
                    </div>
            </div>
            <h4 className="font-weight-light pl-4 pb-1">Parere</h4>
                <div style={{width: "100%"}} className="action-uploader d-flex align-self-start pb-5">
                <FileUpload 
                    className="border-0 flex-column"
                    sz="sm" modal={false} showBtn={false} 
                    getSuccess={getSuccess} mutation={CONSULTAZIONE_VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_CONSULTAZIONE_VAS} disabled={false} 
                    isLocked={false} risorsa={docParere} variables={{codice: uuid, tipo: "consultazione_vas_parere" }}/>
                </div>
            
            <div className="align-self-center mt-7">
                <SalvaInvia mutation={CONSULTAZIONE_VAS_FILE_UPLOAD} canCommit={!!docParere}></SalvaInvia>
            </div>
        </React.Fragment>)
    }

    export default ({codicePiano, utente}) => (
        <Query query={GET_CONSULTAZIONE_VAS} variables={{codice: codicePiano}} onError={showError}>
            {({loading, data: {consultazioneVas: {edges = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI consultazioneSCA={edges[0]} utente={utente}/>)}
            }
        </Query>)