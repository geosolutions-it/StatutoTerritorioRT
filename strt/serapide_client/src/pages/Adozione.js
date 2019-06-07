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

import Elaborati from 'components/ElaboratiAdozione'

import classnames from 'classnames'
import {withControllableState} from 'enhancers'
import {formatDate, showError, getNominativo, filterAndGroupResourcesByUser, map, isEmpty} from 'utils'

import {GET_ADOZIONE_PAGE} from 'schema'





const enhancers = withControllableState('section', 'toggleSection', 'art')

const UI = enhancers(({
    proceduraAdozione: {node: {
        dataDeliberaAdozione, pubblicazioneBurtUrl,
        pubblicazioneBurtData, pubblicazioneSitoUrl,
        pubblicazioneSitoData,
        richiestaConferenzaPaesaggistica,
        risorse: {edges: risorseAdozione=[]} = {}
        } = {}} = {}, 
    pianoContro: {node: {
            risorse: {edges: risorseControdeduzioni= []} ={} } = {}} = {},
    pianoRev: { node: {risorse : {edges: risorsePostCP = []} = {}} = {}} = {},
    vas: { node: { risorse : {edges: risorseVas = []} = {}} = {}} = {},
    piano: {
        autoritaIstituzionali: {edges: aut =[]} = {},
        // altriDestinatari: {edges: dest = []} = {}
    } = {}
    , toggleSection, section} = {}) => {
        
    const controdeduzioni =  risorseAdozione.filter(({node: {tipo, user = {}}}) => tipo === "controdeduzioni").map(({node}) => node)    
    const [{node: deliberaAdozione} = {}]= risorseAdozione.filter(({node: {tipo}}) => tipo === "delibera_adozione")
    const osservazioniEnti =  filterAndGroupResourcesByUser(risorseAdozione, "osservazioni_enti")
    const pareriSca = filterAndGroupResourcesByUser(risorseVas, "parere_sca")
    const [{node: parereMotivato} = {}] = risorseVas.filter(({node: {tipo}}) => tipo === "parere_motivato")
    const [{node: sintesi} = {}] = risorseVas.filter(({node: {tipo}}) => tipo === 'documento_sintesi')
    const [{node: rapporto} = {}] = risorseVas.filter(({node: {tipo}}) => tipo === 'rapporto_ambientale')
    const elaboratiConferenza =  risorseAdozione.filter(({node: {tipo}}) => tipo === 'elaborati_conferenza_paesaggistica').map(({node}) => node)
    
    return (
        <div className="d-flex flex-column pb-4 pt-5">
            <div className="d-flex border-serapide border-top py-5">
                <span className="d-flex mt-4 align-items-center" >
                    <i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{ fontSize: 44}}>library_add</i>
                    <h2 className="m-0 p-2">ADOZIONE</h2>
                </span>
            </div>
            <div className="row pt-5">
                <div className="col-12 py-2">DELIBERA DEL {formatDate(dataDeliberaAdozione)}</div>
                <div className="col-12 py-2">
                        <Risorsa fileSize={false} useLabel resource={deliberaAdozione} isLocked={true}/> 
                        </div>
                <div className="col-12 pt-4">
                    <Elaborati upload={false} risorseAdozione={risorseAdozione} risorseControdeduzioni={risorseControdeduzioni} risorsePostCP={risorsePostCP}></Elaborati>
                </div>
                <div className="border-top w-100 my-5"></div>  
                <div className="col-12 pt-3">DESTINATARI</div>
                <div className="col-6 pt-3 mb-3"><div className="mb-3">SOGGETTI ISTITUZIONALI</div>
                {aut.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 py-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div>
                {/* <div className="col-6 pt-3 pb-3"><div className="mb-3">ALTRI SOGGETTI NON ISTITUZIONALI</div>
                {dest.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 p-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div> */}
                <div className="border-top w-100 my-4"></div>
                <div className="col-4 pb-2">PUBBLICAZIONE B.U.R.T.</div>
                <div className="col-5 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneBurtUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneBurtUrl}</a>    
                </div>
                <div className="col-2">{formatDate(pubblicazioneBurtData)}</div>
                <div className="col-4">PUBBLICAZIONE SITO WEB</div>
                <div className="col-5 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneSitoUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneSitoUrl}</a>
                </div>
                <div className="col-2">{formatDate(pubblicazioneSitoData)}</div>
                <div className="border-serapide border-top w-100 my-4"></div>
            </div>
            <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'art', "text-serapide": section === 'art' })}
                        onClick={() => { toggleSection('art'); }}>
                        ART. 19
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'vas', "text-serapide": section === 'vas' })}
                        onClick={() => { toggleSection('vas'); }}>
                        VAS
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'cpAnte' , "text-serapide": section === 'cpAnte'})}
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
                            <div key={u[0].user.fiscalCode} className="mb-4">
                                <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                                {u.map(parere => (<Risorsa key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Risorsa>))}
                            </div>)) : ( <div className="col-12 samll">Nessuna Osservazione </div>)}
                        </div>
                        <div className="col-auto pt-4">OSSERVAZIONI PRIVATI</div>
                        {risorseAdozione.filter(({node: {tipo}}) => tipo === "osservazioni_privati").map(({node: r}) => (
                            <div  key={r.uuid} className="col-12">
                            <Risorsa className="border-0 mt-2" resource={r}/>
                            </div>
                        ) )}
                        <div className="col-auto pt-4">CONTRODEDUZIONI</div>
                        {controdeduzioni.map((r) => (
                            <div  key={r.uuid} className="col-12">
                            <Risorsa className="border-0 mt-2" resource={r}/>
                            </div>
                        ))}
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
                
        </div>
)})



export default ({piano}) => (
    <Query query={GET_ADOZIONE_PAGE} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {
            pianoControdedotto: {edges: [pianoContro] = []} = {},
            pianoRevPostCp: {edges: [pianoRev] = []} = {},
            procedureAdozione: {edges: [adozione]= []} = {},
            procedureAdozioneVas: {edges: [adozioneVas] = []} = {}}
            }) => {
            if(loading) {
                return (
                    <div className="flex-fill d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>)
            }
            return (
                <UI vas={adozioneVas} proceduraAdozione={adozione} pianoRev={pianoRev} pianoContro={pianoContro} piano={piano}/>)}
        }
    </Query>)