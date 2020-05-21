/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
// import {Input} from 'reactstrap'
import Input from 'components/EnhancedInput'
import Resource from 'components/Resource'
import ActionTitle from 'components/ActionTitle'
import SalvaInvia from 'components/SalvaInvia'
import Spinner from 'components/Spinner'

import  {showError, getCodice, getInputFactory, VAS_DOCS} from 'utils'
import {withControllableState} from 'enhancers'

import {GET_VAS,UPDATE_VAS, PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA_AC, PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA_AP} from 'schema'

const enhancers = withControllableState("url", "onUrlChange","")
const getVasTypeInput = getInputFactory("proceduraVas")

const UI = enhancers(({back, qualificaRichiesta, onUrlChange, vas: {node: {
    pubblicazioneProvvedimentoVerificaAc,
    pubblicazioneProvvedimentoVerificaAp,
    uuid, risorse : {edges: resources = []} = {}} = {}}}) => {
    
    const isAC = qualificaRichiesta === 'AC';
    const provvedimentoVerificaVas  = resources.filter(({node: {tipo, user = {}}}) => tipo === VAS_DOCS.DOC_PRE_VER_VAS).map(({node}) => node).shift()
    const pubblicazione_provvedimento_verifica = isAC ? "pubblicazioneProvvedimentoVerificaAc" : "pubblicazioneProvvedimentoVerificaAp"
    const closeMutation = isAC ? PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA_AC : PUBBLICAZIONE_PROVVEDIMENTO_VERIFICA_AP
    
    return (
        <React.Fragment>
            <ActionTitle>Pubblicazione Provvedimento di Verifica</ActionTitle>
            <Resource useLabel iconSize="icon-15" fontSize="size-11" className="border-0 mt-5" fileSize={false} icon="attach_file" resource={provvedimentoVerificaVas}></Resource>
            
            <span  className="mt-5 d-flex align-items-center">
                <i className="material-icons icon-15 text-serapide pr-2">link</i>
                <Input getInput={getVasTypeInput(uuid, pubblicazione_provvedimento_verifica)} mutation={UPDATE_VAS} disabled={false}
                className="rounded-pill size-10"
                placeholder="Inserire la URL della pagina dove è stato pubblicato il provvedimento di verifica" 
                onChange={undefined} value={isAC ? pubblicazioneProvvedimentoVerificaAc : pubblicazioneProvvedimentoVerificaAp} type="text" />
            </span>
            
            <div className="align-self-center mt-7">
                <SalvaInvia fontSize="size-8" onCompleted={back} mutation={closeMutation} variables={{uuid}} canCommit={pubblicazioneProvvedimentoVerificaAc || pubblicazioneProvvedimentoVerificaAp}></SalvaInvia>
            </div>
        </React.Fragment>)
    })

    export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas}/>)}
            }
        </Query>)