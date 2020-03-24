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
import PianoPageContainer from 'components/PianoPageContainer';
import PianoSubPageTitle from 'components/PianoSubPageTitle';
import {View as Si} from 'components/SoggettiIstituzionali';






const UI = ({
    pubblicazione: { pubblicazioneUrl, pubblicazioneUrlData} = {},
    piano: {
        soggettiOperanti= []
    } = {}
    } = {}) => {

    return (
        <PianoPageContainer>
            <PianoSubPageTitle icon="turned_in" title="PUBBLICAZIONE"/>
            <div className="row pt-5">
                <div className="col-auto py-2">PUBBLICATOI IL {formatDate(pubblicazioneUrlData)}</div>
                <div className="col-auto py-2">URL</div>
                <div className="col-auto py-2 d-flex">
                    <i className="material-icons text-serapide">link</i>
                    <a href={pubblicazioneUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{pubblicazioneUrl}</a>
                </div>
                <div className="border-top w-100 my-5"></div>  
                <div className="col-12 pt-3">DESTINATARI</div>
                <Si soggettiOperanti={soggettiOperanti}/>
                <div className="border-top w-100 my-4"></div>
            </div>
                    
                
        </PianoPageContainer>
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