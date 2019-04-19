/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from "react-apollo"

import FileUpload from 'components/UploadSingleFile'
import Elaborati from 'components/ElaboratiPiano'
import Resource from 'components/Resource'
import {EnhancedListSelector} from 'components/ListSelector'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import AddContact from 'components/AddContact'
import Button from 'components/IconButton'
import TextWithTooltip from 'components/TextWithTooltip'
import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'

import {rebuildTooltip} from 'enhancers'
import  {showError, elaboratiCompletati, getInputFactory, getCodice, getContatti} from 'utils'

import {GET_AVVIO, UPDATE_AVVIO,
    DELETE_RISORSA_AVVIO,
    AVVIO_FILE_UPLOAD, UPDATE_PIANO,
    GET_CONTATTI,
    AVVIA_PIANO
} from 'schema'

const getProceduraAvvioInput = getInputFactory("proceduraAvvio")

const fileProps = {className: `border-0`, mutation: AVVIO_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_AVVIO, disabled: false, isLocked: false}


const UI = rebuildTooltip({onUpdate: false, log: false, comp: "AvvioProc"})(({
    proceduraAvvio: {node: {
            uuid, conferenzaCopianificazione,
            dataScadenzaRisposta,
            garanteNominativo, garantePec,
            risorse: {edges=[]} = {}
            } = {}} = {},
        piano: {
            tipo: tipoPiano = "",
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
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const dests = dest.map(({node: {uuid} = {}} = {}) => uuid)
            const elaboratiCompleti = elaboratiCompletati(tipoPiano, edges)
            return (<React.Fragment>
                <ActionTitle>
                    Avvio del Procedimento<br/><small className="text-nowrap">(Atto di Avvio)<TextWithTooltip dataTip="art. 17 L.R. 65/2014"/></small>
                </ActionTitle>

                <Resource useLabel fileSize={false} className="border-0 mt-3" icon="attach_file" resource={delibera}/>
                <h6 className="pt-5">Elaborati allegati alla delibera di avvio del procedimento <TextWithTooltip dataTip="ai sensi dell’art. 17 comma 3, lett. a,b,c,d,e,f, L.R. 65/2014"/></h6>
                <div className="action-uploader  align-self-start border-bottom">
                <FileUpload
                    {...fileProps}
                    placeholder="Obiettivi del piano"
                    risorsa={obiettivi} variables={{codice: uuid, tipo: "obiettivi_piano" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload
                    {...fileProps}
                    placeholder={(<span>Quadro Conoscitivo<TextWithTooltip dataTip="art. 17, lett.b, L.R. 65/2014"/></span>)}
                    risorsa={quadro} variables={{codice: uuid, tipo: "quadro_conoscitivo" }}/>
                </div>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload
                    {...fileProps}
                    placeholder={(<span>Programma delle attività di informazione e di partecipazione<TextWithTooltip dataTip="art. 17, lett.e, L.R. 65/2014"/></span>)}
                    risorsa={programma} variables={{codice: uuid, tipo: "programma_attivita" }}/>
                </div>


                <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <Elaborati
                            tipoPiano={tipoPiano.toLowerCase()}
                            resources={edges}
                            mutation={AVVIO_FILE_UPLOAD}
                            resourceMutation={DELETE_RISORSA_AVVIO}
                            uuid={uuid}
                           />

                <h5 className="font-weight-light pb-1 mt-5 mb-3">GARANTE DELL'INFORMAZIONE E DELLA PARTECIPAZIONE</h5>
                <Input getInput={getProceduraAvvioInput(uuid, "garanteNominativo")} mutation={UPDATE_AVVIO} disabled={false} className="my-3 rounded-pill" placeholder="Nominativo" onChange={undefined} value={garanteNominativo} type="text" />
                <Input getInput={getProceduraAvvioInput(uuid, "garantePec")} mutation={UPDATE_AVVIO} disabled={false} className="mb-3 rounded-pill" placeholder="Indirizzo Pec" onChange={undefined} value={garantePec} type="email"/>
                <div className="action-uploader  align-self-start border-bottom ">
                <FileUpload
                    {...fileProps}
                    placeholder={(<span>Individuazione del garante dell’informazione e della partecipazione<TextWithTooltip dataTip="art. 17, lett.f, L.R. 65/2014"/></span>)}
                    risorsa={garante} variables={{codice: uuid, tipo: "individuazione_garante_informazione" }}/>
                </div>
                <h5 className="font-weight-light pb-1 mt-5 mb-3">TERMINI SCADENZA PER LA RISPOSTA</h5>
                <EnhancedDateSelector selected={dataScadenzaRisposta ? new Date(dataScadenzaRisposta) : undefined} getInput={getProceduraAvvioInput(uuid, "dataScadenzaRisposta")} className="py-0 rounded-pill" mutation={UPDATE_AVVIO}/>

                <h5 className="font-weight-light pb-1 mt-5">SCELTA SOGGETTI ISTITUZIONALI</h5>
                <h6 className="font-weight-light pb-1">
                        Soggetti istituzionali a cui si chiede il contributo tecnico <TextWithTooltip dataTip="art. 17, lett.c, L.R. 65/2014"/>
                </h6>
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
                                    getList={getContatti}
                                    variables={{}}
                                    onChange={changed}
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
                        <h5 className="font-weight-light pb-1 mt-5">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h5>
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
                                getList={getContatti}
                                variables={{}}
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
                        <h5 className="font-weight-light pb-1 mt-5">RICHIESTA CONFERENZA DI COPIANIFICAZIONE<TextWithTooltip dataTip="art. 25 L.R. 65/2014"/></h5>
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
                                            <span style={{minWidth: 200}}><TextWithTooltip dataTip="art. 25, comma 3 bis L.R. 65/2014" text="SI"/></span>
                                            <input onChange={changed} value="NECESSARIA" checked={conferenzaCopianificazione === "NECESSARIA"} className="form-check-input position-static" type="checkbox"/>
                                            </div>
                                        <div className="d-flex">
                                            <span style={{minWidth: 200}}><TextWithTooltip dataTip="art. 25, comma 3 bis L.R. 65/2014" text="NON ADESSO"/></span>
                                            <input onChange={changed} value="POSTICIPATA" checked={conferenzaCopianificazione === "POSTICIPATA"} className="form-check-input position-static" type="checkbox"/>
                                        </div>
                                        <div className="d-flex">
                                            <span style={{minWidth: 200}}><TextWithTooltip dataTip="art.88, comma 7, lett. c,  e art. 90 comma 7, lett.b, L.R. 65/2014" text="NON NECESSARIA"/></span>
                                            <input onChange={changed} value="NON_NECESSARIA" checked={conferenzaCopianificazione === "NON_NECESSARIA"} className="form-check-input position-static" type="checkbox"/>
                                            <i className={`ml-3 material-icons ${conferenzaCopianificazione === "NON_NECESSARIA" ? "text-serapide" : ""}`}>check_circle_outline</i>
                                            <span className={`pl-1 ${conferenzaCopianificazione === "NON_NECESSARIA" ? "text-serapide" : "text-gray"}`}>NOTIFICA AL GENIO CIVILE</span>
                                        </div>
                                    </div>)}
                            }
                        </Mutation>




                <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={AVVIA_PIANO} canCommit={elaboratiCompleti && obiettivi && quadro && garante && programma && auths.length > 0  && dataScadenzaRisposta && garanteNominativo && garantePec}></SalvaInvia>

                </div>
            </React.Fragment>)})

export default (props) => (
                <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
                    {({loading, data: {procedureAvvio: {edges: [proceduraAvvio] = []} = []} = {}}) => {
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
