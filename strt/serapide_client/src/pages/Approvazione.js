/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import Risorsa from 'components/Resource'
import Elaborati from 'components/ElaboratiPiano'

import {formatDate, showError} from 'utils'

import {GET_APPROVAZIONE_PAGE} from 'schema'

const UI = ({
    approvazione: {
        dataDeliberaApprovazione,
        urlPianoPubblicato,
        pubblicazioneUrl,
        pubblicazioneUrlData,
        risorse: {edges: risorseApprovazione=[]} = {}
        } = {}, 
    adozione: {
        richiestaConferenzaPaesaggistica
        } = {}, 
    piano: {
        autoritaIstituzionali: {edges: aut =[]} = {},
        altriDestinatari: {edges: dest = []} = {}
    } = {}
    } = {}) => {

    
    const [{node: deliberaApprovazione} = {}]= risorseApprovazione.filter(({node: {tipo}}) => tipo === "delibera_approvazione")
    const elaboratiConferenza =  risorseApprovazione.filter(({node: {tipo}}) => tipo === 'elaborati_conferenza_paesaggistica').map(({node}) => node)
    
    return (
        <div className="d-flex flex-column pb-4 pt-5">
            <div className="d-flex border-serapide border-top py-5">
                <span className="d-flex mt-4 align-items-center" >
                    <i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{ fontSize: 44}}>library_add</i>
                    <h2 className="m-0 p-2">APPROVAZIONE</h2>
                </span>
            </div>
            <div className="row pt-5">
                <div className="col-12 py-2">DELIBERA DEL {formatDate(dataDeliberaApprovazione)}</div>
                <div className="col-12 py-2">
                        <Risorsa fileSize={false} useLabel resource={deliberaApprovazione} isLocked={true}/> 
                </div>
                <div className="col-12 mt-3 py-2">ELABORATI PIANO</div>
                <div className="col-12 pt-3">
                    <Elaborati upload={false} resources={risorseApprovazione}></Elaborati>
                </div>
                <div className="border-top w-100 my-5"></div>  
                <div className="col-12 pt-3">DESTINATARI</div>
                <div className="col-6 pt-3 mb-3"><div className="mb-3">SOGGETTI ISTITUZIONALI</div>
                {aut.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 py-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div>
                <div className="col-6 pt-3 pb-3"><div className="mb-3">ALTRI SOGGETTI NON ISTITUZIONALI</div>
                {dest.map(({node: {nome, uuid} = {}}) => (
                        <div className="col-12 px-0 p-1" key={uuid}>
                                 {nome}
                        </div>))}
                </div>
                <div className="border-top w-100 my-4"></div>
                <div className="col-5">PUBBLICAZIONE SITO WEB</div>
                <div className="col-5 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={urlPianoPubblicato} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{urlPianoPubblicato}</a>
                </div>
                <div className="col-2"></div>
                <div className="col-5">PUBBLICAZIONE APPROVAZIONE</div>
                <div className="col-5 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneUrl}</a>
                </div>
                <div className="col-2">{formatDate(pubblicazioneUrlData)}</div>
                <div className="border-serapide border-top w-100 my-4"></div>
            </div>
                    
            {!richiestaConferenzaPaesaggistica ? (
                <div className="row">
                    <div className="col-auto pt-4">ELABORATI CONFERENZA PAESAGGISTICA</div>
                    {elaboratiConferenza.map(r => (
                        <div  key={r.uuid} className="col-12">
                        <Risorsa className="border-0 mt-2" resource={r}/>
                        </div>
                    ) )}
                </div>
                ) : (<div className="row">
                <div className="col-auto pt-4">CONFERENZA PAESAGGISTICA IN ADOZIONE</div>
                </div>) }
                        
           
                
        </div>
)}



export default ({piano}) => (
    <Query query={GET_APPROVAZIONE_PAGE} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {
            pianoRevPostCp: {edges: [{node: pianoRev} = {}] = []} = {},
            procedureApprovazione: {edges: [{node: approvazione} = {}] = []} = {},
            procedureAdozione: {edges: [{node: adozione} = {}]= []} = {}}
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
                <UI  adozione={adozione} approvazione={approvazione} pianoRev={pianoRev} piano={piano}/>)}
        }
    </Query>)