/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
import {Nav, NavItem,NavLink, TabContent,TabPane} from 'reactstrap'

import Risorsa from 'components/Resource'
import VAS from 'components/VAS'

import classnames from 'classnames'
import {withControllableState} from 'enhancers'
import {formatDate, showError} from 'utils'

import {GET_AVVIO, GET_CONFERENZA} from 'schema'





const enhancers = withControllableState('section', 'toggleSection', 'vas')

const UI = enhancers(({
    procedureAvvio: {node: {
        dataScadenzaRisposta,
        garanteNominativo, garantePec,
        risorse: {edges: risorseAvvio = []} = {}
        } = {}} = {}, 
    piano: {
        codice,
        numeroProtocolloGenioCivile,
        dataProtocolloGenioCivile,
        autoritaIstituzionali: {edges: aut =[]} = {},
        altriDestinatari: {edges: dest = []} = {},
        risorse: {edges: risorsePiano = []},
        dataDelibera
    } = {}
    , toggleSection, section} = {}) => {
        
        const {node: delibera} = risorsePiano.filter(({node: n}) => n.tipo === "delibera").shift() || {}
        const {node: obiettivi} = risorseAvvio.filter(({node: {tipo}}) => tipo === "obiettivi_piano").shift() || {}
        const {node: quadro} = risorseAvvio.filter(({node: {tipo}}) => tipo === "quadro_conoscitivo").shift() || {}
        const {node: programma} = risorseAvvio.filter(({node: {tipo}}) => tipo === "programma_attivita").shift() || {}
        const {node: garante } = risorseAvvio.filter(({node: {tipo}}) => tipo === "individuazione_garante_informazione").shift() || {}
        const allegati = risorseAvvio.filter(({node: {tipo}}) => tipo === "altri_allegati_avvio").map(({node}) => node) 
        const integrazioni = risorseAvvio.filter(({node: {tipo}}) => tipo === "integrazioni").map(({node}) => node) 
    return (
        <div className="d-flex flex-column pb-4 pt-5">
            <div className="d-flex border-serapide border-top py-5">
                <span className="d-flex mt-4 align-items-center" >
                    <i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{ fontSize: 44}}>dashboard</i>
                    <h2 className="m-0 p-2">AVVIO DEL PROCEDIMENTO</h2>
                </span>
            </div>
            <div className="row pt-5">
                <div className="col-12 py-2">DELIBERA DEL {formatDate(dataDelibera)}</div>
                <div className="col-12 py-2">
                        <Risorsa fileSize={false} useLabel resource={delibera} isLocked={true}/> 
                        </div>
                
                <div className="col-12 pt-4 pb-2">ELABORATI DEL PIANO</div>
                {obiettivi && quadro && programma && garante ? (
                <React.Fragment>
                <div className="col-12 py-2">
                    <Risorsa fileSize={false} useLabel resource={obiettivi} isLocked={true}/>
                </div>
                <div className="col-12 py-2">
                    <Risorsa fileSize={false} useLabel resource={quadro} isLocked={true}/> 
                </div>
                <div className="col-12 py-2">
                        <Risorsa fileSize={false} useLabel resource={programma} isLocked={true}/>
                </div>
                <div className="col-12 py-2">
                    <Risorsa fileSize={false} useLabel resource={garante} isLocked={true}/> 
                </div>
                </React.Fragment>) : (<div className="col-12 py-2">Nessun elaborato presente</div>)}
                <div className="col-12 pt-4">ALTRI ALLEGATI	
                {allegati.length > 0 ? allegati.map(doc => (	
                    <div key={doc.uuid} className="col-12 px-0 py-2">	
                        <Risorsa fileSize={false}  resource={doc} isLocked={true}/> 	
                </div>)): (<div className="col-12 px-0 py-2">Nessun allegato presente</div>)}	
                </div>
                {integrazioni.length > 0 && (<div className="col-12 pt-4">INTEGRAZIONI
                {integrazioni.map(doc => (
                    <div key={doc.uuid} className="col-12 px-0 py-2">
                        <Risorsa fileSize={false}  resource={doc} isLocked={true}/> 
                </div>))}
                </div>)}
                
                <div className="col-12 pt-4">GARANTE DELL'INFORMAZIONE E DELLA PARTECIAPZIONE
                <div className="col-12 pt-2 pb-1">{garanteNominativo}</div>
                <div className="col-12">{garantePec}</div>
                </div>
                <div className="col-12 d-flex align-items-center pt-4">TERMINI SCADENZA PER LA PROPOSTA{dataScadenzaRisposta && (<span className="p-2 ml-4 border bg-serapide"><i className="material-icons pr-1">date_range</i><span style={{verticalAlign: 'super'}}>{formatDate(dataScadenzaRisposta)}</span></span>)}</div>
                <div className="col-6 pt-4 mb-3"><div className="mb-3">NOTIFICHE SOGGETTI ISTITUZIONALI</div>
                {aut.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 py-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div>
                <div className="col-6 pt-4 pb-3"><div className="mb-3">NOTIFICHE ALTRI SOGGETTI NON ISTITUZIONALI</div>
                {dest.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 p-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div>
            </div>    
            <div className="border-serapide border-top w-100 my-4"></div>   
            
            <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'vas' })}
                        onClick={() => { toggleSection('vas'); }}>
                        VAS
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'conferenza' })}
                        onClick={() => { toggleSection('conferenza'); }}>
                        CONFERENZA COPIANIFICAZIONE
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'genio' })}
                        onClick={() => { toggleSection('genio'); }}>
                        GENIO
                    </NavLink>
                </NavItem>
            </Nav>
            <TabContent activeTab={section}>
                <TabPane tabId="vas">
                    {section === 'vas' && (<div className="row">
                        <div className="col-12 pt-4">
                         <VAS codice={codice} canUpdate={false} isLocked={true}></VAS>
                        </div>
                    </div>)}
                </TabPane>
                <TabPane tabId="conferenza">
                {section === 'conferenza' && (
                    <Query query={GET_CONFERENZA} variables={{codice}} onError={showError}>
                    {({loading, data: {modello: {edges: [conferenza = {}] = []} = {}} = {}, error}) => {
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        const {node: {dataRichiestaConferenza, risorse: {edges: elabConf = []} = {}} = {}} = conferenza
                        const elaboratiConferenza =  elabConf.filter(({node: {tipo}}) => tipo === 'elaborati_conferenza').map(({node}) => node)
                        return (
                        <div className="row pt-4">
                            <div className="col-8 d-flex">
                                <i className="material-icons text-serapide self-align-center">check_circle</i>
                                <span className="pl-1">RICHIESTA CONFERENZA DI COPIANIFICAZIONE</span>
                            </div>
                            <div className="col-4">{!!dataRichiestaConferenza ? formatDate(dataRichiestaConferenza) : "Nessuna richiesta"}</div>
                            <div className="w-100 border-top my-3 border-serapide"></div>
                            <div className="col-12 d-flex">
                                <i className="material-icons text-serapide self-align-center">check_circle</i>
                                <span className="pl-1 pb-2">ESITO</span>
                            </div>
                            <div className="col-auto smoll mb-2">Allegati e Verbali</div>
                            {elaboratiConferenza.length > 0 ? elaboratiConferenza.map(doc => (
                                <div key={doc.uuid} className="col-12 px-0 py-2">
                                    <Risorsa className="border-0" fileSize={false}  resource={doc} isLocked={true}/> 
                                </div>)): (<div className="col-12 px-0 py-2">Nessun documento presente</div>)}
                        </div>)}}
                    </Query>)}
                </TabPane>
                <TabPane tabId="genio">
                    <div className="row pt-4">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide self-align-center">check_circle</i>
                        <span className="pl-1">NOTIFICA DEL GENIO CIVILE</span>
                    </div>
                    
                    </div>
                    {!!numeroProtocolloGenioCivile && (<div className="row pt-4">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide self-align-center">check_circle</i>
                        <span className="pl-1">RICCEZIONE PROTOCOLLO DAL GENIO CIVILE</span>
                    </div>
                    
                    <div className="col-12 pt-3 pl-4 text-serapide">
                    {numeroProtocolloGenioCivile}
                    </div>
                    <div className="col-12 pt-3 pl-4  text-serapide">
                    {!!dataProtocolloGenioCivile && formatDate(dataProtocolloGenioCivile)}
                    </div>
                    </div>)}
                    
                    
                    
                </TabPane>
            </TabContent>
                
        </div>
)})



export default ({back, piano}) => (
    <Query query={GET_AVVIO} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {modello: {edges = []} = {}} = {}}) => {
            if(loading) {
                return (
                    <div className="flex-fill d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>)
            }
            return (
                <UI procedureAvvio={edges[0]} piano={piano}/>)}
        }
    </Query>)