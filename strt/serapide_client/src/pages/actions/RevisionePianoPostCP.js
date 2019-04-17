/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import {Query} from 'react-apollo'
import {GET_PIANO_REV_POST_CP,GET_ADOZIONE,
    PIANO_REV_POST_CP_FILE_UPLOAD,
    DELETE_RISORSA_PIANO_REV_POST_CP,
    REVISONE_CONFERENZA_PAESAGGISTICA
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import Elaborati from '../../components/ElaboratiPiano'
import  {showError,elaboratiCompletati} from '../../utils'


const UI = ({
    back,
    adozione: {node: {uuid: uuidAdo} = {}} = {},
    piano: {tipo: tipoPiano = ""},
    pianoRev: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    }) => {
        const elaboratiCompleti = elaboratiCompletati(tipoPiano, resources)
        return (
            <React.Fragment>
                <ActionTitle>Revisione Piano post C.P.</ActionTitle>
                <h4 className="mt-5 font-weight-light pl-4 pb-1">Elaborati del Piano</h4>
                    <Elaborati 
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={resources}
                        mutation={PIANO_REV_POST_CP_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_PIANO_REV_POST_CP}
                        uuid={uuid}    
                    />

                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuidAdo}} mutation={REVISONE_CONFERENZA_PAESAGGISTICA} canCommit={elaboratiCompleti}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {}, back}) => (
        <Query query={GET_ADOZIONE} variables={{codice: piano.codice}} onError={showError}>
            {({loading: loadingOuter, data: {procedureAdozione: {edges: [adozione] = []} = []} = {}}) => (
                <Query query={GET_PIANO_REV_POST_CP} variables={{codice: piano.codice}} onError={showError}>
                    {({loading, data: {pianoRevPostCp: {edges = []} = []} = {}}) => {
                        if(loading || loadingOuter) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI back={back} piano={piano} adozione={adozione} pianoRev={edges[0]}/>)}
                    }
                </Query>)}
            </Query>)
