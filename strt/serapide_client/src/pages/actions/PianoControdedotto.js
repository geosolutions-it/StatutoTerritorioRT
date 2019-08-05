/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from "react-apollo"

import {EnhancedSwitch} from "components/Switch"
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import Elaborati from 'components/ElaboratiPiano'

import  {showError, getInputFactory, getCodice} from 'utils'

import {GET_ADOZIONE, UPDATE_ADOZIONE,
    PIANO_CONTRODEDOTTO,
    GET_RISORSE_PIANO_CONTRODEDOTTO,
    CONTRODEDOTTO_FILE_UPLOAD, DELETE_RISORSA_CONTRODEDOTTO
} from 'schema'

const getInput = getInputFactory("proceduraAdozione")

const UI = ({
    pianoContro: {node: {
        uuid: uuidContro,
        risorse: {edges = []} ={} } = {}} = {},
    proceduraAdozione: {node: {
            uuid,
            richiestaConferenzaPaesaggistica
            } = {}} = {}, 
        piano: {
            tipo: tipoPiano = ""
            },
        back}) => {
            return (<React.Fragment>
                <ActionTitle>
                  Piano Controdedotto
                </ActionTitle>
                
                <Elaborati
                    iconSize="icon-15"
                    fontSize="size-11"
                    vertical
                    useLabel
                    tipoPiano={tipoPiano.toLowerCase()} 
                    resources={edges}
                    mutation={CONTRODEDOTTO_FILE_UPLOAD}
                    resourceMutation={DELETE_RISORSA_CONTRODEDOTTO}
                    uuid={uuidContro}
                />
                             

                <div className="w-100 border-top mt-3"></div> 

                <div className="row d-flex align-items-center pt-5">
                        <EnhancedSwitch className="switch-small col-2 offset-1" value={true} mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "richiestaConferenzaPaesaggistica")} checked={richiestaConferenzaPaesaggistica}/>
                    <div className="col-9 bg-serapide mb-2"><div className="px-1 py-1 size-14 ">Richiesta Conferenza Paseaggistica</div></div>
                    
                    <div className="col-11 offset-1 text-justify size-13">In base all'ART. 21 - Accordo Regione Toscana-MIBACT
                    il Comune richiede a Regione Toscana di convocare la Conferenza Paesaggistica prima dell'Approvazione del Piano.
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row d-flex align-items-center pt-4">
                    <EnhancedSwitch className="switch-small col-2 offset-1" value={false} mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "richiestaConferenzaPaesaggistica")} checked={!richiestaConferenzaPaesaggistica}/>
                    <div className="col-9 bg-serapide mb-2 "><div className="pl-1 py-1 size-14">Approvazione</div></div>
                    
                    <div className="col-11 offset-1 text-justify size-13">Il Comune richiede direttamente l'Approvazione del Piano.</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={PIANO_CONTRODEDOTTO} 
                        canCommit></SalvaInvia>
                </div>
            </React.Fragment>)}

export default (props) => {
    const codice = getCodice(props)
    return (
    <Query query={GET_RISORSE_PIANO_CONTRODEDOTTO} variables={{codice}} onError={showError}>
        {({loadingContro, data: {modello: {edges: [pianoContro] = []} = []} = {}}) => {
        return (<Query query={GET_ADOZIONE} variables={{codice}} onError={showError}>
                {({loading, data: {modello: {edges: [proceduraAdozione]= []} = []} = {}}) => {
                        if(loading || loadingContro) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI  {...props} pianoContro={pianoContro} proceduraAdozione={proceduraAdozione}/>)}
                    }
        </Query>)}}
    </Query>)
}