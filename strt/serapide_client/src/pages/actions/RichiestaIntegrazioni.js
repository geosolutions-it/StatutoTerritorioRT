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
import {GET_AVVIO,
    UPDATE_AVVIO,
    CHIUSURA_CONFERENZA_COPIANIFICAZIONE
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import {EnhancedSwitch} from '../../components/Switch'
import  {showError} from '../../utils'
import Input from '../../components/EnhancedInput'

const getInput = (uuid) => (val) => ({
    variables: {
        input: { 
            proceduraAvvio: {
                richiestaIntegrazioni: !val}, 
            uuid
        }
    }})
    const getMessaggioInput = (uuid) => (val) => ({
        variables: {
            input: { 
                proceduraAvvio: {
                    messaggioIntegrazioni: val}, 
                uuid
            }
        }})

const UI = ({
    back, 
    proceduraAvvio: {node: {uuid, richiestaIntegrazioni, messaggioIntegrazioni} = {}} = {},
    }) => {    
        
        return (
            <React.Fragment>
                <ActionTitle>Richiesta Integrazioni</ActionTitle>
        
                <div className="row pl-2 pt-4">
                    <div className="col-5 bg-serapide">Richiesta integrazioni</div> 
                    <div className="col-2 ml-2">
                        <EnhancedSwitch className="" value={richiestaIntegrazioni}
                                    getInput={getInput(uuid)}  
                                    ignoreChecked
                                    mutation={UPDATE_AVVIO} checked={richiestaIntegrazioni}/> 
                    </div>        
                </div>
                <div className="row pl-2 pt-4">
                    <Input getInput={getMessaggioInput(uuid)} mutation={UPDATE_AVVIO} disabled={false} placeholder="Inserisci messaggio da inviare" onChange={undefined} value={messaggioIntegrazioni} type="textarea" />
                </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={CHIUSURA_CONFERENZA_COPIANIFICAZIONE} canCommit={false}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({codicePiano,back}) => (
        <Query query={GET_AVVIO} variables={{codice: codicePiano}} onError={showError}>
        {({loading, data: {procedureAvvio: {edges: avvii = []} = []} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} proceduraAvvio={avvii[0]} />)}
            }
        </Query>)