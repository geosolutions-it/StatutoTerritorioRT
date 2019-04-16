/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


import  {showError} from '../../utils'

import {Query} from "react-apollo"

import {EnhancedSwitch} from "../../components/Switch"
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import {getInputFactory} from '../../utils' 
import Input from '../../components/EnhancedInput'


import {GET_ADOZIONE, UPDATE_ADOZIONE,
    PIANO_CONTRODEDOTTO
} from '../../graphql'


const getInput = getInputFactory("proceduraAdozione")

const UI = ({
    proceduraAdozione: {node: {
            uuid,
            urlPianoControdedotto,
            richiestaConferenzaPaesaggistica
            } = {}} = {}, 
        piano: {
            redazioneNormeTecnicheAttuazioneUrl,
            compilazioneRapportoAmbientaleUrl,
            },
        back}) => {
            return (<React.Fragment>
                <ActionTitle>
                  Piano Controdedotto
                </ActionTitle>
                <div className="row">
                    <div className="col-12 pt-2">
                        {`A seguito delle Osservazioni il Comune redige il piano controdedotto utilizzando lo strumento per la redazione
                        delle norme tecniche di attuazione e la compilazione del Rapporto Ambientale (Minerva). Una volta treminata la
                        compilazione del piano controdedotto bisogna inserire  la url nel campo qui di seguito`}
                    </div>
                </div>
                <h6 className="pt-5 font-weight-light">LINK AGLI STRUMENTI PER IL PIANO CONTRODEDOTTO</h6>
                
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={redazioneNormeTecnicheAttuazioneUrl} target="_blank" className="pl-1 text-secondary">Redazione norme tecniche di attuazione</a>
                    </div>
                </div>
                
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={compilazioneRapportoAmbientaleUrl} target="_blank" className="pl-1 text-secondary">Compilazione del Rapporto Ambientale</a>
                    </div>
                </div>
                
                <div className="mt-4 row d-flex align-items-center">
                    <div className="col-1">URL</div>
                    <div className="col-11">
                        <Input placeholder="copiare URL in questo campo" getInput={getInput(uuid, "urlPianoControdedotto")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={urlPianoControdedotto} type="text" />
                    </div>
                </div>

                             

                <div className="w-100 border-top mt-3"></div> 

                <div className="row d-flex align-items-center pt-4">
                    <div className="col-1 offset-1"><EnhancedSwitch value={true} mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "richiestaConferenzaPaesaggistica")} checked={richiestaConferenzaPaesaggistica}/></div>
                    <div className="col-9 bg-serapide"><div className="px-2 py-1  ">Richiesta Conferenza Paseaggistica</div></div>
                    
                    <div className="col-11 offset-1">In base all'ART. 21 - Accordo Regione Toscana-MIBACT
                    il Comune richiede a Regione Toscana di convocare la Conferenza Paesaggistica prima dell'Approvazione del Piano.
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row d-flex align-items-center pt-4">
                    <div className="col-1 offset-1"><EnhancedSwitch value={false} mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "richiestaConferenzaPaesaggistica")} checked={!richiestaConferenzaPaesaggistica}/></div>
                    <div className="col-9 bg-serapide"><div className="pl-2 py-1 ">APPROVAZIONE</div></div>
                    
                    <div className="col-11 offset-1">Il Comune richiede direttamente l'Approvazione del Piano.</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-5">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={PIANO_CONTRODEDOTTO} 
                        canCommit={urlPianoControdedotto}></SalvaInvia>
                </div>
            </React.Fragment>)}

export default ({back, piano}) => (
    
        <Query query={GET_ADOZIONE} variables={{codice: piano.codice}} onError={showError}>
                {({loading, data: {procedureAdozione: {edges = []} = []} = {}}) => {
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI  proceduraAdozione={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)
