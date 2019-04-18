/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import FileUpload from 'components/UploadSingleFile'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import RichiestaComune from 'components/RichiestaComune'

import  {showError, formatDate, daysSub, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE_VAS,
    DELETE_RISORSA_ADOZIONE_VAS,
    ADOZIONE_VAS_FILE_UPLOAD, INVIO_PARERE_MOTIVATO_AC
} from 'schema'


const UI = rebuildTooltip()(({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    scadenza,
    tipo: tipoDoc = "parere_moticato",
    label = "PARERE MOTIVATO AC",
    saveMutation = INVIO_PARERE_MOTIVATO_AC}) => {
        
        const [{node: parere} = {}] = resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc)
        
        return (
            <React.Fragment>
                <ActionTitle>Pareri Motivato AC</ActionTitle>
                <RichiestaComune scadenza={scadenza && daysSub(scadenza, 30)}/>
                <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">{label}</h4>
                <FileUpload 
                    
                    placeholder="Upload file parere"
                    mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_ADOZIONE_VAS} disabled={false} 
                    isLocked={false} risorsa={parere} variables={{codice: uuid, tipo: tipoDoc }}/>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={parere}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

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
        