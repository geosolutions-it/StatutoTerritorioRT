/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import Elaborati from 'components/ElaboratiPiano'

import  {showError, getCodice} from 'utils'

import {GET_PIANO_REV_POST_CP, GET_ADOZIONE,
    PIANO_REV_POST_CP_FILE_UPLOAD,
    DELETE_RISORSA_PIANO_REV_POST_CP,
    REVISONE_CONFERENZA_PAESAGGISTICA
} from 'schema'

const UI = ({
    back,
    deleteRes = DELETE_RISORSA_PIANO_REV_POST_CP,
    uploadRes = PIANO_REV_POST_CP_FILE_UPLOAD,
    saveM = REVISONE_CONFERENZA_PAESAGGISTICA,
    procedura: {node: {uuid: uuidProcedura} = {}} = {},
    piano: {tipo: tipoPiano = ""},
    elab: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    }) => {
        return (
            <React.Fragment>
                <ActionTitle>Revisione Piano post C.P.</ActionTitle>
                <h4 className="mt-5 font-weight-light pl-4 pb-1">Elaborati del Piano</h4>
                    <Elaborati 
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={resources}
                        mutation={uploadRes}
                        resourceMutation={deleteRes}
                        uuid={uuid}    
                    />

                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuidProcedura}} mutation={saveM} canCommit={true}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({outerQuery = GET_ADOZIONE, query = GET_PIANO_REV_POST_CP, ...props}) => {
        const codice = getCodice(props)
        return (
        <Query query={outerQuery} variables={{codice}} onError={showError}>
            {({loading: loadingOuter, data: {modello: {edges: [procedura] = []} = []} = {}}) => (
                <Query query={query} variables={{codice}} onError={showError}>
                    {({loading, data: {modello: {edges: [elab] = []} = []} = {}}) => {
                        if(loading || loadingOuter) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI {...props} procedura={procedura} elab={elab}/>)}
                    }
                </Query>)}
            </Query>)
            }
