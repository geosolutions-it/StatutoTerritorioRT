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
import VAS from 'components/VisualizzaVAS'
import Spinner from 'components/Spinner'

import classnames from 'classnames'
import {withControllableState} from 'enhancers'
import {formatDate, showError, AVVIO_DOCS, getResourceByType, getResourcesByType, PIANO_DOCS} from 'utils'

import {GET_AVVIO_PAGE, GET_CONFERENZA} from 'schema'
import PianoPageContainer from 'components/PianoPageContainer';
import PianoSubPageTitle from 'components/PianoSubPageTitle';
import {View as Si} from 'components/SoggettiIstituzionali';




const enhancers = withControllableState('section', 'toggleSection', 'vas')

const UI = enhancers(({
    procedureAvvio: {node: {
        dataScadenzaRisposta,
        notificaGenioCivile,
        garanteNominativo, garantePec,
        risorse: {edges: risorseAvvio = []} = {}
        } = {}} = {},
    piano: {
        codice,
        dataProtocolloGenioCivile,
        soggettiOperanti = [],
        risorse: {edges: risorsePiano = []},
        dataDelibera,
        numeroDelibera
    } = {}
    , toggleSection, section} = {}) => {

        const delibera = getResourceByType(risorsePiano, PIANO_DOCS.DELIBERA)
        const docProtocollo =  getResourceByType(risorsePiano, PIANO_DOCS.GENIO)

        const obiettivi = getResourceByType(risorseAvvio, AVVIO_DOCS.OBIETTIVI_PIANO)
        const quadro = getResourceByType(risorseAvvio, AVVIO_DOCS.QUADRO_CONOSCITIVO)
        const programma = getResourceByType(risorseAvvio, AVVIO_DOCS.PROGRAMMA_ATTIVITA)
        const garante  = getResourceByType(risorseAvvio, AVVIO_DOCS.INDIVIDUAZIONE_GARANTE_INFORMAZIONE)
        const contributiTecnici  = getResourceByType(risorseAvvio, AVVIO_DOCS.CONTRIBUTI_TECNICI)
        const allegati = getResourcesByType(risorseAvvio, AVVIO_DOCS.ALLEGATI_AVVIO)
        const integrazioni = getResourcesByType(risorseAvvio, AVVIO_DOCS.INTEGRAZIONI)
        
        // const [{node: rapporto} = {}] = risorseVas.filter(({node: {tipo}}) => tipo === 'rapporto_ambientale')
    return (
        <PianoPageContainer>
            <PianoSubPageTitle icon="dashboard" title="AVVIO DEL PROCEDIMENTO"/>
            <div className="row pt-5">
                <div className="col-12 py-2">DELIBERA DEL {formatDate(dataDelibera)}  &nbsp; N° {numeroDelibera ?? " delibera non selezionato"} </div>
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
                <div className="col-12 pt-4 pb-2">CONTRIBUTI TECNICI</div>
                {contributiTecnici && (<div className="col-12 py-2">
                    <Risorsa fileSize={false} useLabel resource={contributiTecnici} isLocked={true}/> 
                </div>)}
                <div className="col-12 pt-4">GARANTE DELL'INFORMAZIONE E DELLA PARTECIAPZIONE
                <div className="col-12 pt-2 pb-1">{garanteNominativo}</div>
                <div className="col-12">{garantePec}</div>
                </div>
                <div className="col-12 d-flex align-items-center pt-4">TERMINI SCADENZA PER LA PROPOSTA{dataScadenzaRisposta && (<span className="p-2 ml-4 border bg-serapide"><i className="material-icons pr-1">date_range</i><span style={{verticalAlign: 'super'}}>{formatDate(dataScadenzaRisposta)}</span></span>)}</div>
                <Si soggettiOperanti={soggettiOperanti}/>
            </div>    
            <div className="border-serapide border-top w-100 my-4"></div>   
            
            <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'vas' }])}
                        onClick={() => { toggleSection('vas'); }}>
                        VAS
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer",{ active: section === 'conferenza' }])}
                        onClick={() => { toggleSection('conferenza'); }}>
                        CONFERENZA COPIANIFICAZIONE
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'genio' }])}
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
                            return <Spinner/>
                        }
                        const {node: {dataRichiestaConferenza, risorse: {edges: elabConf = []} = {}} = {}} = conferenza
                        const elaboratiConferenza =  getResourcesByType(elabConf, AVVIO_DOCS.ELABORATI_CONFERENZA)
                        return (
                        <div className="row pt-4">
                            <div className="col-8 d-flex align-items-center">
                                <span className="pl-1">RICHIESTA CONFERENZA DI COPIANIFICAZIONE</span>
                                <span className="ml-3 font-weight-bold">{!!dataRichiestaConferenza ? `del ${formatDate(dataRichiestaConferenza)}` : "Nessuna richiesta"}</span>
                            </div>
                            
                            <div className="w-100 border-top pt-2 my-3 mx-4 border-serapide"></div>
                            <div className="col-12 d-flex align-items-center">
                                <span className="pl-1 pb-2">DOCUMENTI ALLEGATI E VERBALI</span>
                            </div>
                            
                            {elaboratiConferenza.length > 0 ? elaboratiConferenza.map(doc => (
                                <div key={doc.uuid} className="col-12  py-2">
                                    <Risorsa key={doc.uuid} className="border-0" fileSize={false}  resource={doc} isLocked={true}/> 
                                </div>)): (<div className="col-12 py-2">Nessun documento presente</div>)}
                        </div>)}}
                    </Query>)}
                </TabPane>
                <TabPane tabId="genio">
                    <div className="row pt-4">
                    <div className="col-12 d-flex">
                        <span>NOTIFICA DEL GENIO CIVILE</span>
                        <span className="ml-3 text-serapide font-weight-bold">{!!notificaGenioCivile ? "INVIATA" : "NON INVIATA"}</span>
                    </div>
                    </div>
                    <div className="row pt-4">
                        <div className="col-12 d-flex">
                            <span>DOCUMENTO PROTOCOLLO</span>
                            <span className="ml-3 font-weight-bold">{!docProtocollo && "NON CARICATO"}</span>
                        </div>
                        {!!docProtocollo && <div className="col-12">
                            <Risorsa className="border-0 mt-3" fileSize={false} useLabel resource={docProtocollo} isLocked={true}/>
                        </div>}
                    </div>
                    <div className="row pt-4">
                        {!!dataProtocolloGenioCivile && <div className="col-12 mb-3 d-flex">
                            <span>PROTOCOLLO INVIATO</span>
                            <span className="ml-3">
                            {`il ${formatDate(dataProtocolloGenioCivile)}`}
                            </span>
                        </div>}
                    </div>

                    
                </TabPane>
            </TabContent>
                
            </PianoPageContainer>
)})



export default ({back, piano}) => (
    <Query query={GET_AVVIO_PAGE} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {procedureAvvio: {edges: [avvio] = []} = {}, procedureVas: {edges: [vas] = []} = {}} = {}}) => {
            return loading ? <Spinner/> : <UI procedureAvvio={avvio} vas={vas} piano={piano}/>
            }
        }
    </Query>)