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
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Input from 'components/EnhancedInput'

import {rebuildTooltip} from 'enhancers'
import {showError, getCodice} from 'utils'

import {
    UPDATE_PIANO,
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO
} from 'schema'

const getInput = (codice) => (numeroProtocolloGenioCivile) => ({
    variables: {
            input: { 
                pianoOperativo: { numeroProtocolloGenioCivile},
                codice
            }
        }
    })

const UI = rebuildTooltip()(({ back, 
        piano: {numeroProtocolloGenioCivile, codice} = {}, 
        proceduraAvvio: {node: {uuid} = {}} = {}}
    ) => {
        return (
            <React.Fragment>
                <ActionTitle>Protocollo Genio Civile</ActionTitle>
                
                <ActionParagraphTitle   >
                    <div className="d-flex align-items-center">
                        <i className="material-icons icon-15 rounded-circle text-white bg-serapide">edit</i>
                        <span className="pl-1 text-serapide">INSERISCI PROTOCOLLO</span>
                    </div>
                </ActionParagraphTitle>
                    <div className="px-3 mt-4">
                        <Input className="size-10" placeholder="Numero di protocollo" getInput={getInput(codice)} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={numeroProtocolloGenioCivile} type="text" />
                    </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia  fontSize="size-8" tipIconColor="w" onCompleted={back} variables={{codice: uuid}} mutation={INVIO_PROTOCOLLO_GENIO} canCommit={!!numeroProtocolloGenioCivile}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges:[proceduraAvvio] = []} = {}} = {}, error}) => {
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