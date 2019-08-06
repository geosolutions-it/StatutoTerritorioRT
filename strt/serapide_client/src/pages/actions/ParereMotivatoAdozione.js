/*
 * Copyright 2019, GeoSolutions SAS.
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
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

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
    tipo: tipoDoc = "parere_motivato",
    label = "PARERE MOTIVATO AC",
    saveMutation = INVIO_PARERE_MOTIVATO_AC}) => {
        
        const [{node: parere} = {}] = resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc)
        
        return (
            <React.Fragment>
                <ActionTitle>Pareri Motivato AC</ActionTitle>
                <RichiestaComune fontSize="size-11" iconSize="icon-15" scadenza={scadenza && daysSub(scadenza, 30)}/>
                <div className="mt-4 border-bottom-2 pb-3 d-flex">
                        <i className="material-icons text-serapide pr-3 icon-15">event_busy</i> 
                        <div className="d-flex flex-column size-11">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <ActionParagraphTitle fontWeight="font-weight-light">{label}</ActionParagraphTitle>
                <div className="action-uploader  py-2 align-self-start border-bottom">
                    <FileUpload 
                        className="border-0"
                        iconSize="icon-15" fontSize="size-11" vertical useLabel
                        placeholder="Upload file parere"
                        mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE_VAS} disabled={false} 
                        isLocked={false} risorsa={parere} variables={{codice: uuid, tipo: tipoDoc }}/>
                </div>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={parere}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_ADOZIONE_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [adozioneVas] = []} = []}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={adozioneVas}  />)}
            }
        </Query>)
        