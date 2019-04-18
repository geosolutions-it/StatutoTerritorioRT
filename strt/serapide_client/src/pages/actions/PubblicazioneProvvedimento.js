/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
import {Input} from 'reactstrap'

import Resource from 'components/Resource'
import ActionTitle from 'components/ActionTitle'
import SalvaInvia from 'components/SalvaInvia'

import  {showError, getCodice} from 'utils'
import {withControllableState} from 'enhancers'

import {GET_VAS, PUBBLICA_PROVV_VERIFICA} from 'schema'

const enhancers = withControllableState("url", "onUrlChange","")

const UI = enhancers(({back, url, onUrlChange, vas: {node: {uuid, risorse : {edges: resources = []} = {}} = {}}, utente: {attore}}) => {
    
    const provvedimentoVerificaVas  = resources.filter(({node: {tipo, user = {}}}) => tipo === "provvedimento_verifica_vas").map(({node}) => node).shift()
    const pubblicazione_provvedimento_verifica = attore === 'AC' ? "pubblicazioneProvvedimentoVerificaAc" : "pubblicazioneProvvedimentoVerificaAp"
    return (
        <React.Fragment>
            <ActionTitle>Pubblicazione Provvedimento di Verifica</ActionTitle>
            <Resource className="border-0 mt-2" icon="attach_file" resource={provvedimentoVerificaVas}></Resource>
            
            <span style={{maxWidth: 400}} className="mt-5 d-flex align-items-center">
                <i className="material-icons icon34 text-serapide">link</i>
                    <Input disabled={false} value={url} onChange={(e) => onUrlChange(e.target.value)} type="url" name="text" />                
            </span>
            <span style={{fontSize: "80%", maxWidth: 400}}className="pl-4 font-80">Inserire la URL della pagina dove è stato pubblicato il provvedimento di verifica</span>
            <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} mutation={PUBBLICA_PROVV_VERIFICA} variables={{input: {proceduraVas: {[pubblicazione_provvedimento_verifica]: url}, uuid}}} canCommit={url}></SalvaInvia>
            </div>
        </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {procedureVas: {edges: [vas] = []} = []}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} vas={vas}/>)}
            }
        </Query>)