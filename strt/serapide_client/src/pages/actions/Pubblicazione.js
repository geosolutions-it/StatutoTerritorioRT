/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import ActionTitle from 'components/ActionTitle'
import SalvaInvia from 'components/SalvaInvia'
import Input from 'components/EnhancedInput'
import TextWithTooltip from 'components/TextWithTooltip'
import {EnhancedDateSelector} from 'components/DateSelector'

import  {showError, getCodice, getInputFactory} from 'utils'



const UI = ({
    back,
    title = "Pubblicazione Piano",
    subTitle,
    procedura = "proceduraApprovazione",
    closeAction,
    urlLabel = "URL SITO",
    placeholder = "COPIA URL PIANO",
    updateM,
    piano: {autoritaIstituzionali: {edges: aut =[]} = {},
            // altriDestinatari: {edges: dest = []} = {}
        },
    modello: { node: {uuid, pubblicazioneUrl, pubblicazioneUrlData} = {}} = {}
    }) => {
        const getInput = getInputFactory(procedura)        
        return (
            <React.Fragment>
                <ActionTitle>{title}</ActionTitle>
                <p className="mt-2">{subTitle}</p>
                <div className="mt-4 row d-flex align-items-center mb-1">
                    <div className="col-3">{urlLabel}</div>
                    <div className="col-9 ">
                        <Input placeholder={placeholder} getInput={getInput(uuid, "pubblicazioneUrl")} mutation={updateM} disabled={false}  onChange={undefined} value={pubblicazioneUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneUrlData ? new Date(pubblicazioneUrlData) : undefined} getInput={getInput(uuid, "pubblicazioneUrlData")} className="py-0 " mutation={updateM}/>
                    </div>
                </div>
                <div className="w-100 border-top mt-3"></div>
                <h5 className="pt-4 font-weight-light">DESTINATARI</h5>
                <h6 className="font-weight-light pb-1 mt-2">SOGGETTI ISTITUZIONALI</h6>
                <div className="row">  
                    {aut.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                    </div>
                {/* <h6 className="font-weight-light pb-1 mt-4">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h6>
                <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div> */}
                <div className="w-100 border-top mt-3"></div>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={closeAction} canCommit={pubblicazioneUrl && pubblicazioneUrlData}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({query, ...props}) => (
        <Query query={query} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [modello] = []} = {}}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} modello={modello}/>)}
            }
        </Query>)