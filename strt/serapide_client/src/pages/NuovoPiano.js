/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Button from '../components/IconButton'
import {withPropsOnChange, withStateHandlers, compose} from 'recompose'
import SelectTipo from '../components/SelectTipo'

import { Mutation, Query} from "react-apollo";
import EnteSelector from "../components/EnteSelector"
import { toast } from 'react-toastify'
import {CREA_PIANO, CREA_PIANO_PAGE, GET_PIANI} from '../queries'


/** 
 * TODO:: Manca la gestione errore 
*/
const enhancer = compose(withStateHandlers( ({}),
    {
        selectTipo: () => value => ({tipo: value}),
        selectEnte: () => value => ({ente: value})
    }),
    withPropsOnChange(["isLoading", "isSaving", "enti", "ente", "tipiPiano", "tipo"], ({enti = [], tipiPiano= [], tipo, ...rest}) => {
        return{
        ente: enti.length === 1 && enti[0], tipo: !tipo && tipiPiano.length > 0 ? tipiPiano[0] : tipo, ...rest
    }})
    )
    

const canSubmit = (ente, isLoading, tipo, isSaving) => ente && !isLoading && tipo && !isSaving
const getEnteLabel = ({tipo, nome} = {}) => ( tipo && nome ? `${tipo} di ${nome}` : '')
const getInput = ({node: {code: eCode} = {}} = {}, {value} = {}) => ({ 
        variables: {  
            input: {
                "pianoOperativo": {
                    ente: {code: eCode},
                    tipologia: value
                    }
            }
        }})

//Add newly created piano to piani list
const updateCache = (cache, { data: {createPiano : {nuovoPiano: node}}  = {}} = {}) => {
        try {
            const { piani = {}} = cache.readQuery({ query: GET_PIANI }) || {}     // se la query non è stata eseguita va in errore
            const type = `${node.__typename}Edge`
            piani.edges = piani.edges.concat([{__typename: type, node}]) 
            cache.writeQuery({
                query: GET_PIANI,
                data: { piani}
            })
        } catch (e) {
            console.warn("Query piani non inizializzata")
        }
  }
const Page = enhancer( ({creaPiano, selectTipo, tipo, isLoading, isSaving, enti, ente, selectEnte, tipiPiano}) => {
            return (
                <div>
                    <h4 className="text-uppercase">{getEnteLabel(ente)}</h4>  
                    <div className="row">
                        <div className="col-6">
                            <div className="row pb-4 pt-3">
                                <div className="col-12">
                                    <h3 className="mb-0 d-flex"><i className="material-icons text-serapide icon-34">assignment</i> FORMAZIONE DI UN NUOVO ATTO DEL TERRITORIO</h3>
                                </div>
                                <div style={{paddingLeft: 49, maxWidth: 400}} className="col-sm-12">
                                    {enti && (<EnteSelector className="pt-6" enti={enti} onChange={selectEnte} isLoading={isLoading} value={ente}></EnteSelector>)}
                                    <div className="pt-4 pb-2 font-weight-bold">Atto di governo del territorio</div><br/>
                                    <div className="pb-1 small">Seleziona il tipo di atto</div>
                                    <SelectTipo className="mb-5 text-capitolize" onChange={selectTipo} tipiPiano={tipiPiano} value={tipo} isLoading={isLoading}></SelectTipo>
                                    <Button disabled={!canSubmit(ente, isLoading, tipo, isSaving)} onClick={() => creaPiano(getInput(ente, tipo))}
                                        size='md' tag="a" href="./#/nuovo_piano" 
                                        className="mt-5 flex-column d-flex ext-uppercase align-items-center" 
                                        color="serapide" label="CREA PIANO" isLoading={isSaving}>
                                    </Button>
                                </div>   
                            </div>
                        </div>
                        <div className="col-6">
                            <div className="row pb-4 pt-3">
                                <div className="col-12">
                                    <h5 className="text-uppercase">Istruzioni per la creazione del piano</h5>
                                        <p style={{textAlign: "justify"}}>
                                            In questa sezione è possibile creare un nuovo atto di governo del Territorio e di conseguenza,
                                            aprire il relativo procedimento amministrativo.<br/>Dal menù è possibile
                                            selezionare il tipo di atto per il quale si intende avviare il procedimento (es: Piano Strutturale, Piano Operativo,
                                            Variante)
                                        </p>
                                    </div>
                                <div className="col-12">
                                    <h5 className="text-uppercase">Dcumenti richiesti per la creazione del piano</h5>
                                    <p style={{textAlign: "justify"}}>
                                    Per poter creare l'atto di governo del territorio è necessario compilare una anagrafica del Piano selezionato nella successiva sezione
                                    "CREA ANAGRAFICA". A tal fine è necessario inserire  l’atto amministrativo di avvio del procedimento, specificandone il numero e la sua 
                                    denominazione. Inoltre, sarà necessario indicare se l’atto è assoggettato a VAS (ordinaria o semplificata, secondo le procedure previste dalla L.R. 10/2010)
                                    o se è necessario avviare la procedura di verifica di assoggettabilità (ordinaria o semplificata, secondo le procedure previste dalla L.R. 10/2010) ed allegare.
                                    In ogni caso, i relativii documenti richiesti di avvio alla procedura di VAS dovranno essere caricati in questo momento (Documento preliminare o relazione motivata).
                                    </p>
                                    </div>
                                <div className="col-12">
                                    <h5 className="text-uppercase">Informazioni richieste per la creazione del piano</h5>
                                    <p style={{textAlign: "justify", marginBottom: 0}}>
                                        Per poter procedere correttamente alla creazione del procedimento amministrativo finalizzato all’approvazione dell’atto di governo del territorio,
                                        è necessario essere in possesso delle seguenti informazioni:</p>
                                        <ul className="pt-2">
                                            <li>nominativo RUP</li>
                                            <li>individuazione garante della comunicazione</li>
                                            <li>estremi identificativi dell’atto di avvio del procedimento</li>
                                            <li>procedura di VAS necessaria (secondo quanto previsto dalla L.R. 10/2010)</li>
                                        </ul>
                                    
                                </div>
                            </div>
                        </div>
                    </div>
                </div>)}
            )
export default () => (
    <Query query={CREA_PIANO_PAGE}>
        {({loading: loadingDataQuery, data: {enti: {edges = []} = [] , tipologiaPiano: tipiPiano = []} = {}, error: errorQuery}) => {
            
            if (errorQuery) {
                toast.error(errorQuery.message,  {autoClose: true})
            }
        return (
            <Mutation mutation={CREA_PIANO} onCompleted={({createPiano: {nuovoPiano}} = {}) => window.location.href=`#/crea_anagrafica/${nuovoPiano.codice}`} update={updateCache}>
                {(creaPiano, { loading: isSaving, error: mutationError , ...rest}) => {
                if (mutationError) {
                    toast.error(mutationError.message)
                }
                    return (
                    <Page enti={edges.filter(({node: {role = []} = {}}) => role.indexOf("RUP") !== -1)} tipiPiano={tipiPiano.filter(({value: v}) => v !== "unknown")} creaPiano={creaPiano} isLoading={loadingDataQuery} isSaving={isSaving}/>)}}
            </Mutation>)
            }
        }
    </Query>)