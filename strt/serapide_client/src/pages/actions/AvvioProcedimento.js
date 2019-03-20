/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import  {showError} from '../../utils'
import AutoMutation from '../../components/AutoMutation'
import {Query, Mutation} from "react-apollo"
import Resource from '../../components/Resource'
import {EnhancedListSelector} from '../../components/ListSelector'
import SalvaInvia from '../../components/SalvaInvia'
import AddContact from '../../components/AddContact'
import Button from '../../components/IconButton'
import EnhancedDateSelector from '../../components/DateSelector'

import {Input} from 'reactstrap'
import {GET_CONSULTAZIONE_VAS, CREA_CONSULTAZIONE_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD,
    AVVIO_CONSULTAZIONE_VAS, UPDATE_PIANO,
    GET_CONTATTI
} from '../../queries'




const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success

const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid}}) => ({label: nome, value: uuid}))
}

const UI = ({consultazioneSCA: {node: {avvioConsultazioniSca, dataCreazione, dataScadenza, proceduraVas: {uuid: pVasUUID, tipologia, risorse: {edges=[]} = {} } = {}, uuid} = {}} = {}, piano: {codice, autoritaCompetenteVas: {edges: aut =[]} = {}, soggettiSca: {edges: sca = []} = {}, risorse: {edges: resPiano = []}} = {}, back}) => {
            const dataTermine = new Date()
            const isFull = tipologia === "SEMPLIFICATA" || tipologia === "VERIFICA"
            const {node: delibera} = resPiano.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            
            const docPrelim = edges.filter(({node: {tipo}}) => tipo === "documento_preliminare_vas").map(({node}) => node).shift()
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const scas = sca.map(({node: {uuid} = {}} = {}) => uuid)
            return (<React.Fragment>
                <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Avvio del Procedimento <small>(Atto di Avvio)<br/>documentazione (art. 17 L.R. 65/2014)</small></h2></div>
                <Resource className="border-0 mt-2" icon="attach_file" resource={delibera}/>
                <span className="pt-4">Elaborati del Piano</span>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload 
                    className={`border-0`}
                    sz="sm"
                    placeholder="Delibera di avvio (ai sensi dell’articolo. 17 L.R. 65/2014)"
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload 
                    className={`border-0`}
                    sz="sm"
                    placeholder="Quadro conoscitivo (art. 17, lett.b, L.R. 65/2014)"
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom">
                <FileUpload 
                    className={`border-0`}
                    sz="sm"
                    placeholder="Obiettivi del piano"
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom mb-3">
                <FileUpload 
                    className={`border-0`}
                    sz="sm"
                    placeholder="Obiettivi del piano"
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                <h4 className="font-weight-light pl-2 pb-1">ALTRI ALLEGATI</h4>
                <div className="action-uploader  align-self-start pl-2 pb-5">
                <FileUpload 
                    className={`border-0 ${!docPrelim ? "flex-column": ""}`}
                    sz="sm" modal={false} showBtn={false} 
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                <h5 className="font-weight-light pb-1 mt-3 mb-3">GARANTE DELL'INFORMAZIONE E DELLA PARTECIPAZIONE</h5>
                <Input disabled={false} className="my-3 rounded-pill" placeholder="Nominativo" onChange={undefined} type="text" />
                <Input disabled={false} className="mb-3 rounded-pill" placeholder="Indirizzo Pec" onChange={undefined} type="url"/>
                <h5 className="font-weight-light pb-1 mt-3 mb-3">TERMINI SCADENZA PER LA RISPOSTA</h5>
                <EnhancedDateSelector className="py-0 rounded-pill" selected={dataTermine} mutation={UPDATE_PIANO}/>
                
                <h5 className="font-weight-light pb-1 mt-4">SCELTA SOGGETTI ISTITUZIONALI</h5>
                    {aut.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pl-2 mt-3 " key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                    <div className="mt-4 pl-4 pb-4">
                    <Mutation mutation={UPDATE_PIANO} onError={showError}>
                        {(onChange) => {
                            const changed = (val) => {
                                const autoritaCompetenteVas = auths.indexOf(val) !== -1 ? [] : [val]
                                    onChange({variables:{ input:{ 
                                            pianoOperativo: { autoritaCompetenteVas}, codice}
                                    }})
                            }
                            return (
                                <EnhancedListSelector
                                    selected={auths}
                                    query={GET_CONTATTI}
                                    getList={getAuthorities}
                                    onChange={changed}
                                    variables={{tipo: "acvas"}}
                                    size="lg"
                                    label="SOGGETTI ISTITUZIONALI"
                                    btn={(toggleOpen) => (
                                        <div className="row">
                                            <Button fontSize="60%"  classNameLabel="py-0" onClick={toggleOpen} className="rounded-pill" color="serapide" icon="add_circle" label="Seleziona soggetti istituzionali"/>
                                        </div>
                                        )}

                                    >
                                    <AddContact className="mt-2" tipologia="acvas"></AddContact>
                                    </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <h5 className="font-weight-light pb-1 mt-3">ALTRI DESTINATARI</h5>
                        {sca.map(({node: {nome, uuid} = {}}) => (<div className="d-flex mt-3" key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                        <div className="mt-3 pl-4 border-bottom-2 pb-4 mb-5">
                        <Mutation mutation={UPDATE_PIANO} onError={showError}>
                    {(onChange) => {
                            const changed = (val) => {
                                let nscas = []
                                if(scas.indexOf(val)!== -1){
                                    nscas = scas.filter( uuid => uuid !== val)
                                }else {
                                    nscas = scas.concat(val)
                                }
                                onChange({variables:{ input:{ 
                                            pianoOperativo: { soggettiSca: nscas}, codice}
                                    }})
                            }
                            return (
                        <EnhancedListSelector
                                selected={scas}
                                query={GET_CONTATTI}
                                variables={{tipo: "sca"}}
                                getList={getAuthorities}
                                label="SOGGETTI NON ISTITUZIONALI"
                                size="lg"
                                onChange={changed}
                                btn={(toggleOpen) => (
                                    <div className="row">
                                        <Button fontSize="60%"  classNameLabel="py-0" onClick={toggleOpen} className="rounded-pill" color="serapide" icon="add_circle" label="Aggiungi soggetti non istituzionali"/>
                                    </div>)}
                            >
                            <AddContact className="mt-2" tipologia="sca"></AddContact>
                            </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <h5 className="font-weight-light pb-1 mt-4">RICHIESTA CONFERENZA DI COPIANIFICAZIONE</h5>
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
                        <div className="d-flex flex-column mt-4 pl-2">
                        <div className="d-flex"><span style={{width: 200}}>SI</span><input class="form-check-input position-static" type="checkbox"></input></div>
                        <div className="d-flex"><span style={{width: 200}}>NON ADESSO</span><input class="form-check-input position-static" type="checkbox"></input></div>
                        <div className="d-flex"><span style={{width: 200}}>NON NECESSARIA</span><input class="form-check-input position-static" type="checkbox"></input>
                        <i className="ml-3 material-icons">check_circle_outline</i><span className="pl-1">NOTIFICA AL GENIO CIVILE</span>
                        </div>
                        </div>

                    
                
                <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={AVVIO_CONSULTAZIONE_VAS} canCommit={avvioConsultazioniSca && docPrelim && (!isFull || (auths.length > 0 && scas.length > 0))}></SalvaInvia>
                
                </div>
            </React.Fragment>)}

const updateCache =(codice) => (cache, { data: {createConsultazioneVas : { nuovaConsultazioneVas: node}}  = {}} = {}) => {
    if (node) {
        const consultazioneVas = {__typename: "ConsultazioneVASNodeConnection", edges: [{__typename: "ConsultazioneVASNodeEdge", node}]}
        cache.writeQuery({
                        query: GET_CONSULTAZIONE_VAS,
                        data: { consultazioneVas},
                        variables: {codice}
                    })
    }
}
export default ({codicePiano, back, piano}) => (
                <Query query={GET_CONSULTAZIONE_VAS} variables={{codice: codicePiano}} onError={showError}>
                    {({loading, data: {consultazioneVas: {edges = []} = []} = {}, error}) => {
                        if (!loading && !error && edges.length === 0 && codicePiano) {
                            return (
                                <AutoMutation variables={{input: {codicePiano}}} mutation={CREA_CONSULTAZIONE_VAS} onError={showError} update={updateCache(codicePiano)}>
                                    {() => (
                                        <div className="flex-fill d-flex justify-content-center">
                                            <div className="spinner-grow " role="status">
                                                <span className="sr-only">Loading...</span>
                                            </div>
                                        </div>)}
                                </AutoMutation>)
                        }
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI consultazioneSCA={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)