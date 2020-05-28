/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'
import {Nav, NavItem,NavLink, TabContent,TabPane} from 'reactstrap'

import Risorsa from 'components/Resource'
import PianoSubPageTitle from 'components/PianoSubPageTitle';
import PianoPageContainer from 'components/PianoPageContainer';
import {View as Si} from 'components/SoggettiIstituzionali';
import Spinner from 'components/Spinner'
import Elaborati from 'components/ElaboratiAdozione'

import classnames from 'classnames'
import {withControllableState} from 'enhancers'
import {formatDate, showError, getNominativo,
    filterAndGroupResourcesByUser, map, isEmpty,
    getResourceByType, getResourcesByType, VAS_DOCS,
    ADOZIONE_DOCS} from 'utils'

import {GET_ADOZIONE_PAGE} from 'schema'



const enhancers = withControllableState('section', 'toggleSection', 'art')

const UI = enhancers(({
    proceduraAdozione: {node: {
        dataDeliberaAdozione, pubblicazioneBurtUrl,
        pubblicazioneBurtData, pubblicazioneSitoUrl,
        pubblicazioneBurtBollettino,
        richiestaConferenzaPaesaggistica,
        risorse: {edges: risorseAdozione=[]} = {}
        } = {}} = {}, 
    pianoContro: {node: {
            risorse: {edges: risorseControdeduzioni= []} ={} } = {}} = {},
    pianoRev: { node: {risorse : {edges: risorsePostCP = []} = {}} = {}} = {},
    vasAdozione: { node: { risorse : {edges: risorseVasAdozione = []} = {}} = {}} = {},
    vas: { node: { risorse : {edges: risorseVas = []} = {}} = {}} = {},
    piano: {
        soggettiOperanti = []
    } = {}
    , toggleSection, section} = {}) => {
    
        
    const deliberaAdozione = getResourceByType(risorseAdozione, ADOZIONE_DOCS.DELIBERA)
    const osservazioniEnti =  filterAndGroupResourcesByUser(risorseAdozione, ADOZIONE_DOCS.OSSERVAZIONI_ENTI)
    const osservazioniPrivati = getResourcesByType(risorseAdozione, ADOZIONE_DOCS.OSSERVAZIONI_PRIVATI)
    const controdeduzioni = getResourcesByType(risorseAdozione,ADOZIONE_DOCS.CONTRODEDUZIONI)
    
    const pareriSca = filterAndGroupResourcesByUser(risorseVasAdozione, VAS_DOCS.PAR_SCA_ADOZIONE)
   
    const parereMotivato = getResourceByType(risorseVasAdozione, VAS_DOCS.PARERE_MOTIVATO)
    const sintesi = getResourceByType(risorseVasAdozione, VAS_DOCS.DOCUMENTO_DI_SINTESI)
    const rapporto = getResourceByType(risorseVas, VAS_DOCS.RAPPORTO_AMBIENTALE) 
    const sintesiNon = getResourceByType(risorseVas, VAS_DOCS.SINTESI_NON_TECNICA)
    
    const elaboratiConferenza =  getResourcesByType(risorseAdozione, 'elaborati_conferenza_paesaggistica')
    
    return (
        <PianoPageContainer>
            <PianoSubPageTitle icon="library_add" title="ADOZIONE"/>
                
            
            <div className="row pt-5">
                {dataDeliberaAdozione ? (
                <React.Fragment>
                    <div className="col-12 py-2">DELIBERA DEL {formatDate(dataDeliberaAdozione)}</div>
                    <div className="col-12 py-2">
                        <Risorsa fileSize={false} useLabel resource={deliberaAdozione} isLocked={true}/> 
                    </div>
                </React.Fragment>): (
                    <div className="col-12 py-2">DELIBERA ADOZIONE NON CARICATA NEL SISTEMA</div>)}
                <div className="col-12 pt-4">
                    <Elaborati upload={false} risorseAdozione={risorseAdozione} risorseControdeduzioni={risorseControdeduzioni} risorsePostCP={risorsePostCP}></Elaborati>
                </div>
                <div className="border-top w-100 my-5"></div>  
                <Si useIcon soggettiOperanti={soggettiOperanti}/>
                <div className="border-top w-100 my-5"></div>
                {pubblicazioneBurtUrl && pubblicazioneBurtData ? (
                <React.Fragment>
                    <div className="col-4 pb-2">PUBBLICAZIONE B.U.R.T. N°{pubblicazioneBurtBollettino}</div>
                    <div className="col-5 d-flex">
                        <i className="material-icons text-serapide">link</i>
                        <a href={pubblicazioneBurtUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneBurtUrl}</a>    
                    </div>
                    <div className="col-2">{formatDate(pubblicazioneBurtData)}</div>
                </React.Fragment>) : (<div className="col-12 py-2">ADOZIONE NON ANCORA PUBBLICATA SUL B.U.R.T</div>)}
                {pubblicazioneSitoUrl ? (<React.Fragment>
                <div className="col-4">PUBBLICAZIONE SITO WEB</div>
                <div className="col-5 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneSitoUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneSitoUrl}</a>
                </div>
                </React.Fragment>): (<div className="col-12 py-2">ADOZIONE NON ANCORA PUBBLICATA SUL SITO</div>)}
                
                <div className="border-serapide border-top w-100 my-4"></div>
            </div>
            <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'art', "text-serapide": section === 'art' }])}
                        onClick={() => { toggleSection('art'); }}>
                        ART. 19
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'vas', "text-serapide": section === 'vas' }])}
                        onClick={() => { toggleSection('vas'); }}>
                        VAS
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer",{ active: section === 'cpAnte' , "text-serapide": section === 'cpAnte'}])}
                        onClick={() => { toggleSection('cpAnte'); }}>
                        CONFERENZA PAESAGGISTICA ANTE
                    </NavLink>
                </NavItem>
            </Nav>
            <TabContent activeTab={section}>
                <TabPane tabId="art">
                    {section === 'art' && (
                    <div className="row">
                        <div className="col-auto pt-4">OSSERVAZIONI ENTI</div>
                        <div className="col-12 pt-1">
                        {!isEmpty(osservazioniEnti) ? map(osservazioniEnti, (u) => (
                            <div key={u[0].user.fiscalCode} className="col-12 mb-4">
                                <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                                {u.map(parere => (<Risorsa key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Risorsa>))}
                            </div>)) : ( <div className="col-12 samll">Nessuna Osservazione </div>)}
                        </div>
                        <div className="col-12 pt-4">OSSERVAZIONI PRIVATI
                        {osservazioniPrivati.length > 0 ? osservazioniPrivati.map((r) => (
                            <div  key={r.uuid} className="col-12">
                            <Risorsa className="border-0 mt-2" resource={r}/>
                            </div>
                        ) ) : ( <div className="col-12 samll">Nessuna Osservazione </div>)}
                        </div>
                        <div className="col-12 p-4">CONTRODEDUZIONI
                        {controdeduzioni.map((r) => (
                            <div  key={r.uuid} className="col-12">
                            <Risorsa className="border-0 mt-2" resource={r}/>
                            </div>
                        ))}
                        </div>
                    </div>)}
                </TabPane>
                <TabPane tabId="vas">
                {section === 'vas' && (
                    <div className="row">
                        <div className="col-auto pt-4">PARERI SCA</div>
                        <div className="col-12 pt-1">
                        {pareriSca ? map(pareriSca, (u) => (
                            <div key={u[0].user.fiscalCode} className="mb-4">
                                <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                                {u.map(parere => (<Risorsa key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Risorsa>))}
                            </div>)) : ( <div className="col-12 samll">Nessun parere </div>)}
                        </div>
                        <div className="col-auto pt-4">PARERERE MOTIVATO</div>
                        <div className="col-12 pt-1">
                        {parereMotivato ? <Risorsa className="border-0 mt-2" fileSize={false} useLabel resource={parereMotivato} isLocked={true}/> : ( <div className="col-12 samll">Nessun parere </div>)}
                        </div>
                        <div className="col-auto pt-4">DOCUMENTI DI SINTESI</div>
                        <div className="col-12 pt-1">
                        {sintesi ? <Risorsa className="border-0 mt-2" fileSize={false} useLabel resource={sintesi} isLocked={true}/> : ( <div className="col-12 samll">Nessun documento </div>)}
                        </div>
                        <div className="col-auto pt-4">RAPPORTO AMBIENTALE</div>
                        <div className="col-12 pt-1">
                        {rapporto ? <Risorsa className="border-0 mt-2" fileSize={false} useLabel resource={rapporto} isLocked={true}/> : ( <div className="col-12 samll">Nessun rapporto </div>)}
                        </div>
                        <div className="col-auto pt-4">SINTESI NON TECNICA</div>
                        <div className="col-12 pt-1">
                        {rapporto ? <Risorsa className="border-0 mt-2" fileSize={false} useLabel resource={sintesiNon} isLocked={true}/> : ( <div className="col-12 samll">Nessun sintesi </div>)}
                        </div>
                    </div>

                    )}
                </TabPane>
                <TabPane tabId="cpAnte">
                    
                    {richiestaConferenzaPaesaggistica ? (
                    <div className="row">
                        <div className="col-auto pt-4">ELABORATI CONFERENZA PAESAGGISTICA ANTE</div>
                        {elaboratiConferenza.map(r => (
                            <div  key={r.uuid} className="col-12">
                            <Risorsa className="border-0 mt-2" resource={r}/>
                            </div>
                        ) )}
                    </div>
                    ) : (<div className="row">
                    <div className="col-auto pt-4">CONFERENZA PAESAGGISTICA ANTE NON RICHIESTA</div>
                    </div>) }
                        
                </TabPane>
            </TabContent>   
            </PianoPageContainer>
)})



export default ({piano}) => (
    <Query query={GET_ADOZIONE_PAGE} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {
            pianoControdedotto: {edges: [pianoContro = {}] = []} = {},
            pianoRevPostCp: {edges: [pianoRev = {}] = []} = {},
            procedureAdozione: {edges: [adozione = {}]= []} = {},
            procedureAdozioneVas: {edges: [adozioneVas = {}] = []} = {},
            procedureVas: {edges: [vas = {}] = []} = {}} = {}
            }) => {
                return loading ? (<Spinner/>) : (
                <UI vas={vas} vasAdozione={adozioneVas} proceduraAdozione={adozione} pianoRev={pianoRev} pianoContro={pianoContro} piano={piano}/>)
            }
        }
    </Query>)