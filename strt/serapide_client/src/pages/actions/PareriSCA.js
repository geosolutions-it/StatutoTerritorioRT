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
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import RichiestaComune from '../../components/RichiestaComune'
import  {showError, formatDate, daysSub} from '../../utils'


const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}},
    utente: {fiscalCode} = {},
    scadenza,
    tipoDoc = "parere_verifica_vas",
    tipoVas = "vas_verifica",
    label = "Pareri",
    saveMutation = INVIO_PARERI_VERIFICA}) => {
        
        const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && fiscalCode === user.fiscalCode).map(({node}) => node)
        const documento = resources.filter(({node: {tipo, user = {}}}) => tipo === tipoVas).map(({node}) => node).shift()
        
        return (
            <React.Fragment>
                <ActionTitle>Pareri SCA</ActionTitle>
                <RichiestaComune scadenza={scadenza && daysSub(scadenza, 30)}/>
                <Resource className="border-0 mt-2" icon="attach_file" resource={documento}></Resource>
                <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">{label}</h4>
                <UploadFiles risorse={docsPareri} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false} getSuccess={({uploadRisorsaVas: {success}}) => success} getFileName={({uploadRisorsaVas: {fileName} = {}}) => fileName}/>
                    {/* Se dovessere essere un file singolo
                    <div style={{width: "100%"}} className="action-uploader d-flex align-self-start pb-5">

                    <FileUpload 
                        className="border-0 flex-column"
                        sz="sm" modal={false} showBtn={false} 
                        getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                        isLocked={false} risorsa={docParere} variables={{codice: uuid, tipo: "parere_verifica_vas" }}/>
                    </div> */}
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={docsPareri.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {},  utente, scadenza, back, tipo, label, tipoVas, saveMutation}) => (
        <Query query={GET_VAS} variables={{codice: piano.codice}} onError={showError}>
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
                    <UI back={back} vas={edges[0]} utente={utente} tipoVas={tipoVas} saveMutation={saveMutation} scadenza={scadenza} tipoDoc={tipo} label={label}/>)}
            }
        </Query>)