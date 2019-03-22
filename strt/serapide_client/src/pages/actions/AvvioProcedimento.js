/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import UploadFiles from '../../components/UploadFiles'
import  {showError} from '../../utils'

import {Query, Mutation} from "react-apollo"
import Resource from '../../components/Resource'
import {EnhancedListSelector} from '../../components/ListSelector'
import SalvaInvia from '../../components/SalvaInvia'
import AddContact from '../../components/AddContact'
import Button from '../../components/IconButton'
import {EnhancedDateSelector} from '../../components/DateSelector'

import Input from '../../components/EnhancedInput'

import {GET_AVVIO, UPDATE_AVVIO,
    DELETE_RISORSA_AVVIO,
    AVVIO_FILE_UPLOAD,
    AVVIO_CONSULTAZIONE_VAS, UPDATE_PIANO,
    GET_CONTATTI,
    AVVIA_PIANO
} from '../../queries'


const getGaranteInput = (uuid) => (val) => ({
    variables: {
        input: { 
            proceduraAvvio: {
                garanteNominativo: val}, 
            uuid
        }
    }})
const getGarantePecInput = (uuid) => (val) => ({
        variables: {
            input: { 
                proceduraAvvio: {
                    garantePec: val}, 
            uuid
        }
}})
const getScadenzaInput = (uuid) => (val) => ({
    variables: {
        input: { 
            proceduraAvvio: {
                dataScadenzaRisposta: val.toISOString()},
            uuid
        }
    }})

const getSuccess = ({uploadRisorsaAvvio: {success}} = {}) => success

const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid, tipologia}}) => ({label: nome, value: uuid, tipologia}))
}

const UI = ({
    procedureAvvio: {node: {
            uuid, conferenzaCopianificazione, 
            dataCreazione, dataScadenzaRisposta,
            garanteNominativo, garantePec,
            risorse: {edges=[]} = {}
            } = {}} = {}, 
        piano: {
            autoritaIstituzionali: {edges: aut =[]} = {},
            altriDestinatari: {edges: dest = []} = {},
            codice,    
            risorse: {edges: resPiano = []}} = {}, 
        back}) => {

            const {node: delibera} = resPiano.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            const obiettivi = edges.filter(({node: {tipo}}) => tipo === "obiettivi_piano").map(({node}) => node).shift()
            const quadro = edges.filter(({node: {tipo}}) => tipo === "quadro_conoscitivo").map(({node}) => node).shift()
            const programma = edges.filter(({node: {tipo}}) => tipo === "programma_attivita").map(({node}) => node).shift()
            const garante = edges.filter(({node: {tipo}}) => tipo === "individuazione_garante_informazione").map(({node}) => node).shift()
            const allegati = edges.filter(({node: {tipo}}) => tipo === "altri_allegati_avvio").map(({node}) => node)
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const dests = dest.map(({node: {uuid} = {}} = {}) => uuid)

            return (<React.Fragment>
                <div  className="py-3 border-bottom-2 border-top-2 mb-3"><h2 className="m-0">Avvio del Procedimento <small>(Atto di Avvio)<br/>documentazione (art. 17 L.R. 65/2014)</small></h2></div>
                
                <h6>Delibera di avvio</h6>
                <Resource className="border-0 mt-2" icon="attach_file" resource={delibera}/>
                <h6 className="pt-5">Elaborati allegati alla delibera di avvio del procedimento</h6>
                <div className="action-uploader  align-self-start border-bottom">
                <FileUpload 
                    className={`border-0`}
                    placeholder="Obiettivi del piano"
                    getSuccess={getSuccess} mutation={AVVIO_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_AVVIO} disabled={false} 
                    isLocked={false} risorsa={obiettivi} variables={{codice: uuid, tipo: "obiettivi_piano" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload 
                    className={`border-0`}
                    placeholder="Quadro conoscitivo"
                    getSuccess={getSuccess} mutation={AVVIO_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_AVVIO} disabled={false} 
                    isLocked={false} risorsa={quadro} variables={{codice: uuid, tipo: "quadro_conoscitivo" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload 
                    className={`border-0`}
                    placeholder="Programma delle attività di informazione ai cittadini"
                    getSuccess={getSuccess} mutation={AVVIO_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_AVVIO} disabled={false} 
                    isLocked={false} risorsa={programma} variables={{codice: uuid, tipo: "programma_attivita" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload 
                    className={`border-0`}
                    placeholder="Individuazione del garante dell'informazione"
                    getSuccess={getSuccess} mutation={AVVIO_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_AVVIO} disabled={false} 
                    isLocked={false} risorsa={garante} variables={{codice: uuid, tipo: "individuazione_garante_informazione" }}/>
                </div>
                
                <h4 className="font-weight-light pt-5 pl-2 pb-1">ALTRI ALLEGATI</h4>
                <UploadFiles 
                    risorse={allegati} 
                    mutation={AVVIO_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_AVVIO}
                    variables={{codice: uuid, tipo: "altri_allegati_avvio" }}
                    isLocked={false} getSuccess={getSuccess} getFileName={({uploadRisorsaAvvio: {fileName} = {}}) => fileName}/>
                
                
                <h5 className="font-weight-light pb-1 mt-5 mb-3">GARANTE DELL'INFORMAZIONE E DELLA PARTECIPAZIONE</h5>
                <Input getInput={getGaranteInput(uuid)} mutation={UPDATE_AVVIO} disabled={false} className="my-3 rounded-pill" placeholder="Nominativo" onChange={undefined} value={garanteNominativo} type="text" />
                <Input getInput={getGarantePecInput(uuid)} mutation={UPDATE_AVVIO} disabled={false} className="mb-3 rounded-pill" placeholder="Indirizzo Pec" onChange={undefined} value={garantePec} type="url"/>
                
                <h5 className="font-weight-light pb-1 mt-5 mb-3">TERMINI SCADENZA PER LA RISPOSTA</h5>
                <EnhancedDateSelector selected={dataScadenzaRisposta ? new Date(dataScadenzaRisposta) : undefined} getInput={getScadenzaInput(uuid)} className="py-0 rounded-pill" mutation={UPDATE_AVVIO}/>
                
                <h5 className="font-weight-light pb-1 mt-5">SCELTA SOGGETTI ISTITUZIONALI</h5>
                    <div className="row">  
                    {aut.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                    </div>
                    <div className="mt-3 pl-4 pb-4">
                    <Mutation mutation={UPDATE_PIANO} onError={showError}>
                        {(onChange) => {
                            const changed = (val) => {
                                let autoritaIstituzionali = []
                                if(auths.indexOf(val)!== -1){
                                    autoritaIstituzionali = auths.filter( uuid => uuid !== val)
                                }else {
                                    autoritaIstituzionali = auths.concat(val)
                                }
                                    onChange({variables:{ input:{ 
                                            pianoOperativo: { autoritaIstituzionali}, codice}
                                    }})
                            }
                            return (
                                <EnhancedListSelector
                                    selected={auths}
                                    query={GET_CONTATTI}
                                    getList={getAuthorities}
                                    onChange={changed}
                                    variables={{}}
                                    size="lg"
                                    label="SOGGETTI ISTITUZIONALI"
                                    btn={(toggleOpen) => (
                                        <div className="row">
                                            <Button fontSize="60%"  classNameLabel="py-0" onClick={toggleOpen} className="rounded-pill" color="serapide" icon="add_circle" label="Seleziona soggetti istituzionali"/>
                                        </div>
                                        )}
                                    >
                                    <AddContact className="mt-2"></AddContact>
                                    </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <h5 className="font-weight-light pb-1 mt-5">ALTRI DESTINATARI</h5>
                        <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div>
                        <div className="mt-3 pl-4 border-bottom-2 pb-4 mb-5">
                        <Mutation mutation={UPDATE_PIANO} onError={showError}>
                    {(onChange) => {
                            const changed = (val) => {
                                let altriDestinatari = []
                                if(dests.indexOf(val)!== -1){
                                    altriDestinatari = dests.filter( uuid => uuid !== val)
                                }else {
                                    altriDestinatari = dests.concat(val)
                                }
                                onChange({variables:{ input:{ 
                                            pianoOperativo: { altriDestinatari}, codice}
                                    }})
                            }
                            return (
                        <EnhancedListSelector
                                selected={dests}
                                query={GET_CONTATTI}
                                variables={{}}
                                getList={getAuthorities}
                                label="SOGGETTI NON ISTITUZIONALI"
                                size="lg"
                                onChange={changed}
                                btn={(toggleOpen) => (
                                    <div className="row">
                                        <Button fontSize="60%"  classNameLabel="py-0" onClick={toggleOpen} className="rounded-pill" color="serapide" icon="add_circle" label="Aggiungi soggetti non istituzionali"/>
                                    </div>)}
                            >
                            <AddContact className="mt-2"></AddContact>
                            </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <h5 className="font-weight-light pb-1 mt-5">RICHIESTA CONFERENZA DI COPIANIFICAZIONE</h5>
                        <div className="row pl-2">
                            <div className="col-12 pt-2">
                                Se si seleziona l'opzione "Si" viene inviata a Regione Toscana la RICHIESTA
                                    di convocazione della Conferenza di Copianificazione.<br/>
                                Se si seleziona l'opzione "Non Adesso" il sistema inserisce nella lista delle attività la Conferenza di Copianificazione
                                    come attività da espletare.
                                <br/>
                                    Se si seleziona l'opzione "Non necessaria" il sistema invierà i documenti al Genio Civile 
                                    per il deposito e nella lista delle attività verrà indicata la Ricezione del Protocollo
                                    dal Genio Civile come attività in attesa di risposta.
                                
                            </div>
                        </div>
                        <Mutation mutation={UPDATE_AVVIO} onError={showError}>
                            {(onChange) => {
                                const changed = (e) => {
                                    onChange({
                                        variables:{ 
                                            input:{ 
                                                proceduraAvvio: {conferenzaCopianificazione: e.target.value.toLowerCase()}, 
                                                uuid
                                            }
                                        }})
                                }   
                                return (
                                    <div className="d-flex flex-column mt-4 pl-2">
                                        <div className="d-flex">
                                            <span style={{minWidth: 200}}>SI</span>
                                            <input onChange={changed} value="NECESSARIA" checked={conferenzaCopianificazione === "NECESSARIA"} className="form-check-input position-static" type="checkbox"/>
                                            </div>
                                        <div className="d-flex">
                                            <span style={{minWidth: 200}}>NON ADESSO</span>
                                            <input onChange={changed} value="POSTICIPATA" checked={conferenzaCopianificazione === "POSTICIPATA"} className="form-check-input position-static" type="checkbox"/>
                                        </div>
                                        <div className="d-flex">
                                            <span style={{minWidth: 200}}>NON NECESSARIA</span>
                                            <input onChange={changed} value="NON_NECESSARIA" checked={conferenzaCopianificazione === "NON_NECESSARIA"} className="form-check-input position-static" type="checkbox"/>
                                            <i className={`ml-3 material-icons ${conferenzaCopianificazione === "NON_NECESSARIA" ? "text-serapide" : ""}`}>check_circle_outline</i>
                                            <span className={`pl-1 ${conferenzaCopianificazione === "NON_NECESSARIA" ? "text-serapide" : "text-gray"}`}>NOTIFICA AL GENIO CIVILE</span>
                                        </div>
                                    </div>)}
                            }
                        </Mutation>
                        

                    
                
                <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={AVVIA_PIANO} canCommit={obiettivi && quadro && garante && programma && auths.length > 0 && dests.length > 0 && dataScadenzaRisposta && garanteNominativo && garantePec}></SalvaInvia>
                
                </div>
            </React.Fragment>)}

export default ({back, piano}) => (
                <Query query={GET_AVVIO} variables={{codice: piano.codice}} onError={showError}>
                    {({loading, data: {procedureAvvio: {edges = []} = []} = {}, error}) => {
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI procedureAvvio={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)