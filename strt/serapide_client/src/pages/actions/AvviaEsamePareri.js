/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
import className from "classnames"

import Switch from 'components/Switch'
import Resource from 'components/Resource'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import {map} from 'lodash'
import  {showError, getNominativo, getCodice, filterAndGroupResourcesByUser} from 'utils'
import {toggleControllableState} from 'enhancers'

import {GET_VAS,
    AVVIO_ESAME_PARERI_SCA
} from 'schema'


const enhancer = toggleControllableState('checked', 'toggleSwitch', false)


const UI = enhancer(({
    back, 
    vas: {node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    checked,
    toggleSwitch}) => {
        
        const pareriUser =  filterAndGroupResourcesByUser(resources, "parere_sca")
        const docpreliminare =  resources.filter(({node: {tipo}}) => tipo === "documento_preliminare_vas").map(({node}) => node).shift()
    
    return (
        <React.Fragment>
            <ActionTitle>Avvia Esame Pareri SCA</ActionTitle>
            <ActionParagraphTitle fontWeight="font-weight-light">DOCUMENTO PRELIMINARE</ActionParagraphTitle>
            <Resource iconSize="icon-15" fontSize="size-11" vertical useLabel className="border-0" icon="attach_file" resource={docpreliminare}></Resource>
            
            <ActionParagraphTitle fontWeight="font-weight-light">PARERI SCA</ActionParagraphTitle>
            <div className={className(" mb-5", {"border-bottom-2": pareriUser.length > 0})}>
            {map(pareriUser, (u) => (
                <div key={u[0].user.fiscalCode} className="mb-4">
                    <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                    {u.map(parere => (<Resource icon2Size="icon-15" fontSize="size-11" vertical useLabel  key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Resource>))}
                </div>
                ))
                }
            </div>
        
            <div className="d-flex align-items-center switch-small ">
                <i className="material-icons text-serapide icon-15 pr-2">email</i>
                <div className="bg-serapide px-2 size-12">Avvia consultazione SCA</div>                    
                <Switch
                    labelClassName = "col-auto"
                    checked={checked}
                    toggleSwitch={toggleSwitch}
                    ignoreChecked/> 
            </div>           
            <div className="pt-2 size-13 text-justify">Nota: Selezionare l'opzione Avvia Esame Pareri non comporta nessuna comunicazione
                    agli altri attori coinvolti nel procedimento VAS e nessuna scadenza predefinita. E' solo una funzione per 
                    tenere traccia e evidenziare lo stato di avanzamento del procedimento.
            </div>
                                    
            <div className="align-self-center mt-7">
                <SalvaInvia fontSize="size-8" onCompleted={back} mutation={AVVIO_ESAME_PARERI_SCA} variables={{uuid}} canCommit={checked}></SalvaInvia>
            </div>
        </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}} = {}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas}/>)}
            }
        </Query>)