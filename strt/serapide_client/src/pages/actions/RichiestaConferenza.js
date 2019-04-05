/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {
    RICHIESTA_CONFERENZA_COPIANIFICAZIONE,
    UPDATE_PIANO,
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO
} from '../../queries'
import {FormGroup, Input, Label} from 'reactstrap'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import {toggleControllableState} from '../../enhancers/utils'
import {Query} from 'react-apollo'
import {showError} from '../../utils'

const enhancer = toggleControllableState("isChecked", "toggleCheck", false)

const getInput = (codice) => (numeroProtocolloGenioCivile) => (
    {variables:{ input:{ 
    pianoOperativo: { numeroProtocolloGenioCivile}, codice}
}})
const UI = enhancer(({ back, 
    procedureAvvio: {node: {
        uuid}} = {},
        isChecked,
        toggleCheck
    }) => {
        
        return (
            <React.Fragment>
                <ActionTitle>Conferenza di copianificazione</ActionTitle>
                
                <h5 className="mt-4 font-weight-light"><i className="material-icons pr-1">question_answer</i>RICHIESTA CONFERENZA COPIANIFICAZIONE</h5>
                <FormGroup className="py-4 px-5" check>
                    <Label check>
                        <Input className="text-serapide" type="checkbox" checked={isChecked} onChange={toggleCheck}/>
                        Selezionando questa opzione viene inviata richiesta a Regione Toscana di convocazione
                        della Conferenza di Copianificazione.
                    </Label>
                </FormGroup>     
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={RICHIESTA_CONFERENZA_COPIANIFICAZIONE} canCommit={isChecked}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default ({back, piano}) => (
        <Query query={GET_AVVIO} variables={{codice: piano.codice}} onError={showError}>
            {({loading, data: {procedureAvvio: {edges = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI procedureAvvio={edges[0]} back={back} piano={piano}/>)}
            }
        </Query>)