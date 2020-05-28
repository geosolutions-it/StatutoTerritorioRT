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

import {GET_ADOZIONE,ADOZIONE_FILE_UPLOAD,
    DELETE_RISORSA_ADOZIONE,ESITO_CONFERENZA_PAESAGGISTICA
} from 'schema'


const UI = ({
    back,
    saveM = ESITO_CONFERENZA_PAESAGGISTICA,
    uploadM = ADOZIONE_FILE_UPLOAD,
    deleteM = DELETE_RISORSA_ADOZIONE,
    procedura: {node: {
        uuid,
        risorse: {edges=[]} = {}
        } = {}} = {}
    }) => {    
        const docsAllegati =  edges.filter(({node: {tipo, user = {}}}) => tipo === 'elaborati_conferenza_paesaggistica').map(({node}) => node)
        return (
            <React.Fragment>
                <ActionTitle>Esisto Conferenza Paesaggistica</ActionTitle>
                <ActionParagraphTitle fontWeight="font-weight-light">Verbali e Allegati</ActionParagraphTitle>
                <UploadFiles
                        iconSize="icon-15"
                        fontSize="size-11"
                        vertical
                        useLabel
                        risorse={docsAllegati} 
                        mutation={uploadM} 
                        resourceMutation={deleteM}
                        variables={{codice: uuid, tipo: 'elaborati_conferenza_paesaggistica' }}
                        isLocked={false}/>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={saveM} canCommit={docsAllegati.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({getM = GET_ADOZIONE, ...props}) => (
        <Query query={getM} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [procedura] = []} = []} = {}}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} procedura={procedura}/>)}
            }
        </Query>)