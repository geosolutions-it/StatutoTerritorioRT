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
import {EnhancedSwitch} from 'components/Switch'
import Input from 'components/EnhancedInput'

import {rebuildTooltip} from 'enhancers'
import  {showError, getCodice, getInputFactory} from 'utils'

import {GET_AVVIO,
    UPDATE_AVVIO,
    RICHIESTA_INTEGRAZIONI
} from 'schema'

const getInput = getInputFactory("proceduraAvvio")

const UI = rebuildTooltip()(({
    back, 
    proceduraAvvio: {node: {uuid, richiestaIntegrazioni, messaggioIntegrazione} = {}} = {},
    }) => {    
        
        return (
            <React.Fragment>
                <ActionTitle>Richiesta Integrazioni</ActionTitle>
        
                <div className="row pl-2 pt-4">
                    <div className="col-5 bg-serapide">Richiesta integrazioni</div> 
                    <div className="col-2 ml-2">
                        <EnhancedSwitch className="" value={!richiestaIntegrazioni}
                                    getInput={getInput(uuid, "richiestaIntegrazioni")}  
                                    ignoreChecked
                                    mutation={UPDATE_AVVIO} checked={richiestaIntegrazioni}/> 
                    </div>        
                </div>
                <div className="row pl-2 pt-4">
                    <Input getInput={getInput(uuid, "messaggioIntegrazione")} mutation={UPDATE_AVVIO} disabled={false} placeholder="Inserisci messaggio da inviare" onChange={undefined} value={messaggioIntegrazione} type="textarea" />
                </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={RICHIESTA_INTEGRAZIONI} canCommit={!!messaggioIntegrazione}></SalvaInvia>
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
                    <UI {...props} proceduraAvvio={proceduraAvvio} />)}
            }
        </Query>)