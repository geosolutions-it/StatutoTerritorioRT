/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import UploadFiles from '../../components/UploadFiles'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import RichiestaComune from '../../components/RichiestaComune'

import  {showError, formatDate, daysSub, getCodice} from '../../utils'

import {GET_ADOZIONE_VAS,
    DELETE_RISORSA_ADOZIONE_VAS,
    ADOZIONE_VAS_FILE_UPLOAD, INVIO_PARERI_ADOZIONE
} from '../../graphql'


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    scadenza,
    tipo: tipoDoc = "parere_sca",
    label = "Pareri",
    saveMutation = INVIO_PARERI_ADOZIONE}) => {
        
        const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && fiscalCode === user.fiscalCode).map(({node}) => node)
        
        
        return (
            <React.Fragment>
                <ActionTitle>Pareri SCA</ActionTitle>
                <RichiestaComune scadenza={scadenza && daysSub(scadenza, 30)}/>
                <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">{label}</h4>
                <UploadFiles risorse={docsPareri} 
                        mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE_VAS}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false}/>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={docsPareri.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default (props) => (
        <Query query={GET_ADOZIONE_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {procedureAdozioneVas: {edges: [adozioneVas] = []} = []}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} vas={adozioneVas}  />)}
            }
        </Query>)
        