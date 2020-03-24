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
import RichiestaComune from 'components/RichiestaComune'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import  {showError, formatDate, daysSub, getCodice} from 'utils'

import {GET_ADOZIONE_VAS,
    DELETE_RISORSA_ADOZIONE_VAS,
    ADOZIONE_VAS_FILE_UPLOAD, INVIO_PARERI_ADOZIONE
} from 'schema'


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    scadenza,
    tipo: tipoDoc = "parere_adozione_sca",
    label = "Pareri",
    saveMutation = INVIO_PARERI_ADOZIONE}) => {
        
        const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && fiscalCode === user.fiscalCode).map(({node}) => node)
        
        
        return (
            <React.Fragment>
                <ActionTitle>Pareri SCA</ActionTitle>
                <RichiestaComune fontSize="size-11" iconSize="icon-15" scadenza={scadenza && daysSub(scadenza, 30)}/>
                <div className="mt-4 border-bottom-2 pb-3 d-flex">
                        <i className="material-icons text-serapide pr-3 icon-15">event_busy</i> 
                        <div className="d-flex flex-column size-11">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <ActionParagraphTitle fontWeight="font-weight-light">{label}</ActionParagraphTitle>
                <UploadFiles
                        iconSize="icon-15" fontSize="size-11" vertical useLabel
                        risorse={docsPareri} 
                        mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE_VAS}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false}/>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={docsPareri.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default (props) => (
        <Query query={GET_ADOZIONE_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [adozioneVas] = []} = {}}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={adozioneVas}  />)}
            }
        </Query>)
        