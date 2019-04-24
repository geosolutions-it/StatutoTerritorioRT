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
import {EnhancedDateSelector} from 'components/DateSelector'

import  {showError, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_AVVIO, UPDATE_AVVIO,
    DELETE_RISORSA_AVVIO,
    AVVIO_FILE_UPLOAD, INTEGRAZIONI_RICHIESTE
} from 'schema'

const getInput = getInputFactory("proceduraAvvio")

const UI = rebuildTooltip()(({
    back, 
    proceduraAvvio: {node: {
        uuid, 
        dataScadenzaRisposta,
        risorse: {edges=[]} = {}
        } = {}} = {}, 
    }) => {
        
        const integrazioni =  edges.filter(({node: {tipo, user = {}}}) => tipo === "integrazioni").map(({node}) => node)
        
        
        return (
            <React.Fragment>
                <ActionTitle>Integrazioni Richieste</ActionTitle>
                <div className="row">
                <div className="col-12 d-flex align-items-center">
                        <i className="material-icons icon-18 rounded-circle text-white bg-serapide">edit</i>
                        <span className="pl-1 text-serapide">CARICA FILES PER L'INTEGRAZIONE</span>
                    </div>
                    </div>
                <UploadFiles risorse={integrazioni} 
                        mutation={AVVIO_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_AVVIO}
                        variables={{codice: uuid, tipo: 'integrazioni' }}
                        isLocked={false}/>
                    <h5 className="font-weight-light pb-1 mt-5 mb-3">TERMINI SCADENZA PER LA RISPOSTA</h5>
                <EnhancedDateSelector selected={dataScadenzaRisposta ? new Date(dataScadenzaRisposta) : undefined} getInput={getInput(uuid, "dataScadenzaRisposta")} className="py-0 rounded-pill" mutation={UPDATE_AVVIO}/>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={INTEGRAZIONI_RICHIESTE} canCommit={integrazioni.length> 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [proceduraAvvio] = []} = {}} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} proceduraAvvio={proceduraAvvio}/>)}
                    }
        </Query>)