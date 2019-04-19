/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import UploadFiles from 'components/UploadFiles'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import Elaborati from "components/ElaboratiPiano"

import  {showError, formatDate, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD, TRASMISSIONE_OSSERVAZIONI
} from 'schema'


const UI = rebuildTooltip()(({
    disableSave = false,
    showData = true ,
    back, 
    // piano: {tipo: tipoPiano = ""} = {},
    proceduraAdozione: { node: {uuid, dataRicezionePareri, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    titolo = "Osservazioni Privati",
    tipo: tipoDoc = "osservazioni_privati",
    label = "CARICA I FILES DELLE OSSERVAZIONI DEI PRIVATI",
    filterByUser = true,
    saveMutation = TRASMISSIONE_OSSERVAZIONI}) => {
        
        const osservazioni =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && (!filterByUser || fiscalCode === user.fiscalCode)).map(({node}) => node)

        
        return (
            <React.Fragment>
                <ActionTitle>{titolo}</ActionTitle>
                {showData && (<div className="mt-4 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{dataRicezionePareri && formatDate(dataRicezionePareri, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale inviare le osservazioni</span>
                        </div>
                </div>)}
                <h4 className="mt-5 font-weight-light pl-4 pb-1">{label}</h4>
                <UploadFiles risorse={osservazioni} 
                        mutation={ADOZIONE_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false}/>
                {/* <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <Elaborati 
                    tipoPiano={tipoPiano.toLowerCase()} 
                    resources={resources}
                    mutation={ADOZIONE_FILE_UPLOAD}
                    resourceMutation={DELETE_RISORSA_ADOZIONE}
                    uuid={uuid}
                           />         */}
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={osservazioni.length> 0 && !disableSave}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_ADOZIONE} variables={{codice: getCodice(props)}} onError={showError}>
             {({loading, data: {procedureAdozione: {edges: [proceduraAdozione] = []} = []} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} proceduraAdozione={proceduraAdozione} />)}
            }
        </Query>)