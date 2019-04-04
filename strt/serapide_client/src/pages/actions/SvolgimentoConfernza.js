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
import ActionTitle from '../../components/ActionTitle'
import RichiestaComune from '../../components/RichiestaComune'
import  {showError, formatDate, daysSub} from '../../utils'


const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    tipoDoc = "parere_verifica_vas",
    label = "Verbali e Allegati",
    saveMutation = INVIO_PARERI_VERIFICA}) => {
        
        const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && fiscalCode === user.fiscalCode).map(({node}) => node)
        
        
        return (
            <React.Fragment>
                <ActionTitle>Svolgimento Conf. Copianificazione</ActionTitle>
                <h4 className="mt-5 font-weight-light pl-4 pb-1">{label}</h4>
                <UploadFiles risorse={docsPareri} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false} getSuccess={({uploadRisorsaVas: {success}}) => success} getFileName={({uploadRisorsaVas: {fileName} = {}}) => fileName}/>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={docsPareri.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({codicePiano, utente, scadenza, back, tipo, label, tipoVas, saveMutation}) => (
        <Query query={GET_VAS} variables={{codice: codicePiano}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []} = {}, error}) => {
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