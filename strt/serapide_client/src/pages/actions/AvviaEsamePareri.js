/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Switch from '../../components/Switch'
import Resource from '../../components/Resource'
import {Query, Mutation} from 'react-apollo'

import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import className from "classnames"
import {map} from 'lodash'
import {GET_VAS,
    AVVIO_ESAME_PARERI_SCA
} from '../../queries'
import  {showError, getNominativo} from '../../utils'
import {toggleControllableState} from '../../enhancers/utils'

const enhancer = toggleControllableState('checked', 'toggleSwitch', false)




const UI = enhancer(({
    back, 
    vas: {node: {uuid, assoggettamento, tipologia, risorse : {edges: resources = []} = {}} = {}} = {},
    checked,
    toggleSwitch}) => {
    const pareriUser =  resources.filter(({node: {tipo}}) => tipo === "parere_sca").reduce((acc, {node}) => {
        if (acc[node.user.fiscalCode]) { 
            acc[node.user.fiscalCode].push(node)
        }
        else {
            acc[node.user.fiscalCode] = [node]
        }
        return acc
    } , {})

    const docpreliminare =  resources.filter(({node: {tipo}}) => tipo === "documento_preliminare_vas").map(({node}) => node).shift()
    return (
        <React.Fragment>
            <ActionTitle>Avvia Esame Pareri SCA</ActionTitle>
            <h5 className="font-weight-light mt-4">DOCUMENTO PRELIMINARE</h5>
            <Resource className="border-0 mt-2" icon="attach_file" resource={docpreliminare}></Resource>
            
            <h5 className="font-weight-light mt-4">PARERI SCA</h5>
            <div className={className(" mb-4", {"border-bottom-2": pareriUser.length > 0})}>
            {map(pareriUser, (u) => (
                <div key={u[0].user.fiscalCode} className="mb-4">
                    <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                    {u.map(parere => (<Resource key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Resource>))}
                </div>
                ))
                }
            </div>
            <div className="row pl-2">
                <div className="col-12">
                    <div className="col-12 d-flex pl-0">
                        <i className="material-icons text-serapide pr-3">email</i>
                                <div className="bg-serapide mb-auto px-2">Avvia esame pareri sca</div>
                                <Switch 
                                    checked={checked}
                                    toggleSwitch={toggleSwitch}
                                    ignoreChecked
                                /> 
                    </div>
                            
                    <div className="col-12 pt-2">Nota: Selezionale l'opzione Avvia Esame Pareri non comporta nessuna cmunicazione
                            agli altri attori coinvolti nel procedimento VAS e nessuna scadenza predefinita. E' solo una funzione per 
                            tentere traccia e evidenziare lo stato di avanzamento del procedimento.
                    </div>
                        
                </div>
            </div> 
            
            
            <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} mutation={AVVIO_ESAME_PARERI_SCA} variables={{uuid}} canCommit={checked}></SalvaInvia>
            </div>
        </React.Fragment>)
    })

    export default ({codicePiano, scadenza, back}) => (
        <Query query={GET_VAS} variables={{codice: codicePiano}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} vas={edges[0]} scadenza={scadenza}/>)}
            }
        </Query>)