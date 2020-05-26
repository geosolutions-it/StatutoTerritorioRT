/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from "react-apollo"



import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'

import Spinner from 'components/Spinner'

import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'


import  {showError, formatDate, getInputFactory, getCodice} from 'utils'


import {GET_ADOZIONE, UPDATE_ADOZIONE,
    PUBBLICAZIONE_BURT
} from 'schema'
 

const getInput = getInputFactory("proceduraAdozione")
                    
const UI = (({
    proceduraAdozione: {node: {
            uuid,
            scadenzaPareriAdozioneSca,
            pubblicazioneBurtUrl,
            pubblicazioneBurtData, pubblicazioneSitoUrl,
            pubblicazioneBurtBollettino
            } = {}} = {}, 
        piano: {
            codice
            },
        back}) => {                   
            return (<React.Fragment>
                <ActionTitle>
                   Pubblicazione Adozione
                </ActionTitle>             
                <ActionParagraphTitle>B.U.R.T</ActionParagraphTitle>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3 size-12">NUMERO</div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder="NUMERO BOLLETTINO B.U.R.T." getInput={getInput(uuid, "pubblicazioneBurtBollettino")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneBurtUrl} type="text" />
                    </div>
                    <div className="col-3 size-12">DATA</div>
                    <div className="col-9 mt-2">
                    <EnhancedDateSelector  placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneBurtData ? new Date(pubblicazioneBurtData) : undefined} getInput={getInput(uuid, "pubblicazioneBurtData")} className="py-0 rounded-pill size-8 icon-13" mutation={UPDATE_ADOZIONE}/>
                    </div>
                    <div className="col-3 size-12 mt-2">URL</div>
                    <div className="col-9 mt-2">
                        <Input className="size-10" placeholder="COPIA URL B.U.R.T." getInput={getInput(uuid, "pubblicazioneBurtUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneBurtUrl} type="text" />
                    </div>     
                </div>
                <ActionParagraphTitle>SITO</ActionParagraphTitle>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3 size-12">URL SITO</div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder="COPIA URL SITO" getInput={getInput(uuid, "pubblicazioneSitoUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneSitoUrl} type="text" />
                    </div>
                </div>
                <div className="w-100 border-top mt-3"></div>    
                <ActionParagraphTitle className="mb-0 font-weight-light">INVIO A SCA E AC</ActionParagraphTitle>

                
                <div className="pt-3 text-justify size-13">
                    {`Il sistema invierà i link ai Soggetti Compententi in materia ambientale e all'Autorità compentente
                    in materia ambientale (già selezionati nella fase di avvio) la documentazione necessaria affinché i destinatari
                    possano formulare i pareri entro 60gg dall'adozione`}
                </div>
                <div className="w-100 border-top mt-3"></div> 

                <div className="row d-flex align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide icon-16">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-dark text-serapide size-13">ALERT RICEZIONI OSSERVAZIONI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-dark pr-1 icon-16">date_range</i><span>{scadenzaPareriAdozioneSca && formatDate(scadenzaPareriAdozioneSca)}</span></div>
                    <div className="col-11 offset-1 size-12">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide icon-18">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-serapide size-13">ALERT RICEZIONI PARERI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-serapide pr-1 icon-16">date_range</i><span>{scadenzaPareriAdozioneSca && formatDate(scadenzaPareriAdozioneSca)}</span></div>
                    <div className="col-11 offset-1 size-12">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di adozione</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={PUBBLICAZIONE_BURT} 
                        canCommit={ pubblicazioneBurtUrl && pubblicazioneBurtData && pubblicazioneSitoUrl && pubblicazioneBurtBollettino}></SalvaInvia>
                </div>
            </React.Fragment>)})

export default (props) => {
    const codice = getCodice(props)
    return (
        <Query query={GET_ADOZIONE} variables={{codice}} onError={showError}>
            {({loading, data: { modello: {edges: [proceduraAdozione] = []} = {}, modelloVas: {edges: [vas] = []} = {}} = {} }) => {
                return loading ? <Spinner/> : <UI {...props} vas={vas} proceduraAdozione={proceduraAdozione} />
                }
            }
        </Query>)
    }
        