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
import ListaContatti from 'components/ListaContatti'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

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
                    <div className="col-3 size-12">{urlLabel}</div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder={placeholder} getInput={getInput(uuid, "pubblicazioneUrl")} mutation={updateM} disabled={false}  onChange={undefined} value={pubblicazioneUrl} type="text" />
                    </div>
                </div>
                <ActionParagraphTitle fontWeight="font-weight-light" className="pb-1 d-flex justify-content-between size-12">
                    <span className="my-auto">DATA PUBBLICAZIONE</span>
                    <EnhancedDateSelector popperPlacement="left" placeholder="SELEZIONA DATA" selected={pubblicazioneUrlData ? new Date(pubblicazioneUrlData) : undefined} getInput={getInput(uuid, "pubblicazioneUrlData")} className="py-0 ml-2 rounded-pill size-8 icon-13" mutation={updateM}/>
                </ActionParagraphTitle>
                
                <div className="w-100 border-top mt-3"></div>
                <ActionParagraphTitle className="pt-4 font-weight-light">DESTINATARI</ActionParagraphTitle>
                <ListaContatti title="SOGGETTI ISTITUZIONALI" contacts={aut}/>
                {/* <h6 className="font-weight-light pb-1 mt-4">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h6>
                <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div> */}
                <div className="w-100 border-top mt-3"></div>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={closeAction} canCommit={pubblicazioneUrl && pubblicazioneUrlData}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({query, ...props}) => (
        <Query query={query} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [modello] = []} = {}}}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} modello={modello}/>)}
            }
        </Query>)