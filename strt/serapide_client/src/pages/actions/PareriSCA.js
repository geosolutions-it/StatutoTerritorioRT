/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import UploadFiles from '../../components/UploadFiles'
import Resource from '../../components/Resource'
import {Query} from 'react-apollo'
import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD, INVIO_PARERI_VERIFICA
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import  {showError, formatDate, daysSub} from '../../utils'

const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({back, vas: {node: {uuid, documentoPreliminareVerifica, risorse : {edges: resources = []} = {}} = {}}, utente: {fiscalCode} = {}, scadenza}) => {
    const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === "parere_verifica_vas" && fiscalCode === user.fiscalCode).map(({node}) => node)
    return (
        <React.Fragment>
            <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Pareri SCA</h2></div>
            <div className="d-flex mb-3 mt-3 justify-content-between">
                <div className="d-flex">
                    <i className="material-icons text-serapide">check_circle_outline</i>
                    <span className="pl-2">Richiesta Comune</span>
                </div>
                <div>{scadenza && formatDate(daysSub(scadenza, 30), "dd MMMM yyyy")}</div>
            </div>
            <Resource className="border-0 mt-2" icon="attach_file" resource={documentoPreliminareVerifica}></Resource>
            <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                    <i className="material-icons text-serapide pr-3">event_busy</i> 
                    <div className="d-flex flex-column">
                        <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                        <span>Data entro la quale ricevere i pareri</span>
                    </div>
            </div>
            <h4 className="font-weight-light pl-4 pb-1">Pareri</h4>
            <UploadFiles risorse={docsPareri} 
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS}
                    variables={{codice: uuid, tipo: "parere_verifica_vas" }}
                    isLocked={false} getSuccess={({uploadRisorsaVas: {success}}) => success} getFileName={({uploadRisorsaVas: {fileName} = {}}) => fileName}/>
                {/* <div style={{width: "100%"}} className="action-uploader d-flex align-self-start pb-5">

                <FileUpload 
                    className="border-0 flex-column"
                    sz="sm" modal={false} showBtn={false} 
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docParere} variables={{codice: uuid, tipo: "parere_verifica_vas" }}/>
                </div> */}
            
            <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={INVIO_PARERI_VERIFICA} canCommit={docsPareri.length> 0}></SalvaInvia>
            </div>
        </React.Fragment>)
    }

    export default ({codicePiano, utente, scadenza, back}) => (
        <Query query={GET_VAS} variables={{codice: codicePiano}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} vas={edges[0]} utente={utente} scadenza={scadenza}/>)}
            }
        </Query>)