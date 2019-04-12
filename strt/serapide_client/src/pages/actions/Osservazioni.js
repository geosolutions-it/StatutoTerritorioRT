/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import UploadFiles from '../../components/UploadFiles'
import {Query} from 'react-apollo'
import {GET_ADOZIONE,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD, INVIO_PARERI_VERIFICA
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import  {showError, formatDate, daysSub} from '../../utils'


const UI = ({
    back, 
    proceduraAdozione: { node: {uuid, dataRicezionePareri, risorse : {edges: resources = []} = {}} = {}},
    utente: {fiscalCode} = {},
    titolo = "Osservazioni Privati",
    tipoDoc = "osservazioni_privati",
    label = "CARICA I FILES DELLE OSSERVAZIONI DEI PRIVATI",
    filterByUser = true,
    saveMutation = INVIO_PARERI_VERIFICA}) => {
        
        const osservazioni =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && (!filterByUser || fiscalCode === user.fiscalCode)).map(({node}) => node)

        
        return (
            <React.Fragment>
                <ActionTitle>{titolo}</ActionTitle>
                <div className="mt-4 mb-5 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{dataRicezionePareri && formatDate(dataRicezionePareri, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale inviare le osservazioni</span>
                        </div>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">{label}</h4>
                <UploadFiles risorse={osservazioni} 
                        mutation={ADOZIONE_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false} getSuccess={({uploadRisorsaAdozione: {success}}) => success} getFileName={({uploadRisorsaAdozione: {fileName} = {}}) => fileName}/>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={osservazioni.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {},  filterByUser, titolo, utente, back, tipo, label, saveMutation}) => (
        <Query query={GET_ADOZIONE} variables={{codice: piano.codice}} onError={showError}>
             {({loading, data: {procedureAdozione: {edges = []} = []} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} filterByUser={filterByUser}  titolo={titolo} proceduraAdozione={edges[0]} utente={utente} saveMutation={saveMutation} tipoDoc={tipo} label={label}/>)}
            }
        </Query>)