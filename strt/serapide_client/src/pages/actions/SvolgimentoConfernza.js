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
import Spinner from 'components/Spinner'

import  {showError, getCodice} from 'utils'

import {GET_CONFERENZA,GET_AVVIO,
    DELETE_RISORSA_COPIANIFICAZIONE,
    CONFEREZA_FILE_UPLOAD, CHIUSURA_CONFERENZA_COPIANIFICAZIONE
} from 'schema'

const UI = ({
    back, 
    proceduraAvvio: {node: {uuid: avvioId, richiestaIntegrazioni} = {}} = {},
    conferenza: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    }) => {    
        const docsAllegati =  resources.filter(({node: {tipo, user = {}}}) => tipo === 'elaborati_conferenza').map(({node}) => node)
        return (
            <React.Fragment>
                <ActionTitle>Svolgimento Conf. Copianificazione</ActionTitle>
                <ActionParagraphTitle fontWeight="font-weight-light">Verbali e Allegati</ActionParagraphTitle>
                <UploadFiles 
                        iconSize="icon-15" fontSize="size-11" vertical useLabel
                        risorse={docsAllegati} 
                        mutation={CONFEREZA_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_COPIANIFICAZIONE}
                        variables={{codice: uuid, tipo: 'elaborati_conferenza' }}
                        isLocked={false}/>

                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: avvioId}} mutation={CHIUSURA_CONFERENZA_COPIANIFICAZIONE} canCommit={docsAllegati.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default (props) => {
        const codice = getCodice(props)
        return (
        <Query query={GET_AVVIO} variables={{codice}} onError={showError}>
            {({loding: loadingOut, data: {modello: {edges: [proceduraAvvio] = []} = {}} = {}}) => {
            return (
        <Query query={GET_CONFERENZA} variables={{codice}} onError={showError}>
            {({loading, data: {modello: {edges: [conferenza] = []} = []} = {}}) => {
                if(loading || loadingOut) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} proceduraAvvio={proceduraAvvio} conferenza={conferenza}/>)}
            }
        </Query>)}}
        </Query>)}