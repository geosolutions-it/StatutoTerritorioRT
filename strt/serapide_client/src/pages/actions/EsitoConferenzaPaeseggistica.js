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
import {GET_ADOZIONE,ADOZIONE_FILE_UPLOAD,
    DELETE_RISORSA_ADOZIONE,ESITO_CONFERENZA_PAESAGGISTICA
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'

import  {showError} from '../../utils'


const UI = ({
    back, 
    proceduraAdozione: {node: {
        uuid,
        risorse: {edges=[]} = {}
        } = {}} = {}
    }) => {    
        const docsAllegati =  edges.filter(({node: {tipo, user = {}}}) => tipo === 'elaborati_conferenza_paesaggistica').map(({node}) => node)
        return (
            <React.Fragment>
                <ActionTitle>Esisto Conferenza Paesaggistica</ActionTitle>
                <h4 className="mt-5 font-weight-light pl-4 pb-1">Verbali e Allegati</h4>
                <UploadFiles risorse={docsAllegati} 
                        mutation={ADOZIONE_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        variables={{codice: uuid, tipo: 'elaborati_conferenza_paesaggistica' }}
                        isLocked={false}/>


                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={ESITO_CONFERENZA_PAESAGGISTICA} canCommit={docsAllegati.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {}, back}) => (
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
                    <UI back={back} piano={piano} proceduraAdozione={edges[0]}/>)}
            }
        </Query>)