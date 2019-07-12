/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import {formatDate, showError} from 'utils'

import {GET_PUBBLICAZIONE} from 'schema'







const UI = ({
    pubblicazione: { pubblicazioneUrl, pubblicazioneUrlData} = {},
    piano: {
        autoritaIstituzionali: {edges: aut =[]} = {},
        // altriDestinatari: {edges: dest = []} = {}
    } = {}
    } = {}) => {

    return (
        <div className="d-flex flex-column pb-4 pt-5">
            <div className="d-flex border-serapide border-top py-5">
                <span className="d-flex mt-4 align-items-center" >
                    <i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{ fontSize: 44}}>turned_in</i>
                    <h2 className="m-0 p-2">PUBBLICAZIONE</h2>
                </span>
            </div>
            <div className="row pt-5">
                <div className="col-auto py-2">PUBBLICATOI IL {formatDate(pubblicazioneUrlData)}</div>
                <div className="col-auto py-2">URL</div>
                <div className="col-auto py-2 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneUrl}</a>
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
            </div>
                    
                
        </div>
)}



export default ({piano}) => (
    <Query query={GET_PUBBLICAZIONE} variables={{codice: piano.codice}} onError={showError}>
        {({loading, data: {modello: {edges: [{node: modello} = {}] = []} = {}}}) => {
            if(loading) {
                return (
                    <div className="flex-fill d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>)
            }
            return (
                <UI  pubblicazione={modello} piano={piano}/>)}
        }
    </Query>)