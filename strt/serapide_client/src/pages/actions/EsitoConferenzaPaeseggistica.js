/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import UploadFiles from '../../components/UploadFiles'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'

import  {showError, getCodice} from '../../utils'

import {GET_ADOZIONE,ADOZIONE_FILE_UPLOAD,
    DELETE_RISORSA_ADOZIONE,ESITO_CONFERENZA_PAESAGGISTICA
} from '../../graphql'

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
                    <UI {...props} proceduraAdozione={proceduraAdozione}/>)}
            }
        </Query>)