/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import Input from '../../components/EnhancedInput'

import {showError, getCodice} from '../../utils'

import {
    UPDATE_PIANO,
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO
} from '../../graphql'

const getInput = (codice) => (numeroProtocolloGenioCivile) => ({
    variables: {
            input: { 
                pianoOperativo: { numeroProtocolloGenioCivile},
                codice
            }
        }
    })

const UI = ({ back, 
    piano: {numeroProtocolloGenioCivile, codice} = {}, 
    proceduraAvvio: {node: {uuid}} = {}}) => {
        
        return (
            <React.Fragment>
                <ActionTitle>Protocollo Genio Civile</ActionTitle>
                
                <div className="mt-4 row d-flex">
                    <div className="col-12 d-flex align-items-center">
                        <i className="material-icons icon-18 rounded-circle text-white bg-serapide">edit</i>
                        <span className="pl-1 text-serapide">INSERISCI PROTOCOLLO</span>
                    </div>
                    <div className="col-11 px-3 mt-3 offset-1">
                        <Input getInput={getInput(codice)} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={numeroProtocolloGenioCivile} type="text" />
                    </div>
                </div>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={INVIO_PROTOCOLLO_GENIO} canCommit={!!numeroProtocolloGenioCivile}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {procedureAvvio: {edges:[proceduraAvvio] = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} procedureAvvio={proceduraAvvio}/>)}
            }
        </Query>)