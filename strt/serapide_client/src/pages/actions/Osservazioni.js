/*
 * Copyright 2019, GeoSolutions SAS.
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
import ActionParagraphTitle from 'components/ActionParagraphTitle'

import  {showError, formatDate, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD, TRASMISSIONE_OSSERVAZIONI
} from 'schema'

const UI = rebuildTooltip()(({
    disableSave = false,
    hideSave = false,
    showData = true,
    filterByUser = true,
    back, 
    proceduraAdozione: { node: {uuid, dataRicezionePareri, risorse : {edges: resources = []} = {}} = {}},
    utente: {fiscalCode} = {},
    titolo = "Osservazioni Privati",
    tipo: tipoDoc  = "osservazioni_privati",
    label = "CARICA I FILES DELLE OSSERVAZIONI DEI PRIVATI",
    saveMutation = TRASMISSIONE_OSSERVAZIONI}) => {
        
        const osservazioni =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && (!filterByUser || fiscalCode === user.fiscalCode)).map(({node}) => node)

        
        return (
            <React.Fragment>
                <ActionTitle>{titolo}</ActionTitle>
                {showData && (<div className="mt-4 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide icon-18 pr-3">event_busy</i> 
                        <div className="d-flex flex-column size-14">
                            <span>{dataRicezionePareri && formatDate(dataRicezionePareri, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale inviare le osservazioni</span>
                        </div>
                </div>)}
                <ActionParagraphTitle fontWeight="font-weight-light">{label}</ActionParagraphTitle>
                <UploadFiles 
                        iconSize="icon-15"
                        fontSize="size-11"
                        vertical
                        useLabel
                        risorse={osservazioni} 
                        mutation={ADOZIONE_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false}/>
                
                {!hideSave && (<div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={osservazioni.length> 0 && !disableSave}></SalvaInvia>
                </div>)}
            </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_ADOZIONE} variables={{codice: getCodice(props)}} onError={showError}>
             {({loading, data: {modello: {edges: [proceduraAdozione] = []} = []} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} proceduraAdozione={proceduraAdozione}/>)}
            }
        </Query>)
