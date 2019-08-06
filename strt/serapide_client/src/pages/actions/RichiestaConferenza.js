/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
import {FormGroup, Input, Label} from 'reactstrap'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import {toggleControllableState} from 'enhancers'
import {showError, getCodice} from 'utils'

import {
    RICHIESTA_CONFERENZA_COPIANIFICAZIONE,
    GET_AVVIO
} from 'schema'

const enhancer = toggleControllableState("isChecked", "toggleCheck", false)

const UI = enhancer(({ back, 
    proceduraAvvio: {node: {
        uuid}} = {},
        isChecked,
        toggleCheck
    }) => {
        
        return (
            <React.Fragment>
                <ActionTitle>Conferenza di copianificazione</ActionTitle>
                
                <ActionParagraphTitle fontWeight="font-weight-light">
                    <i className="material-icons icon-15 pr-1">question_answer</i>RICHIESTA CONFERENZA COPIANIFICAZIONE
                    </ActionParagraphTitle>
                <FormGroup className="pt-4 px-5" check>
                    <Label className="size-12" check>
                        <Input className="text-serapide size-11" type="checkbox" checked={isChecked} onChange={toggleCheck}/>
                        Selezionando questa opzione viene inviata richiesta a Regione Toscana di convocazione
                        della Conferenza di Copianificazione.
                    </Label>
                </FormGroup>     
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={RICHIESTA_CONFERENZA_COPIANIFICAZIONE} canCommit={isChecked}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [proceduraAvvio] = []} = {}} = {}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} proceduraAvvio={proceduraAvvio}/>)}
            }
        </Query>)