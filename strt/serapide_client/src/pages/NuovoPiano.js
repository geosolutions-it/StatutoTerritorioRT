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
                        <div className="d-flex flex-column flex-eql ">
                            <h4 className="text-uppercase">{getEnteLabel(ente)}</h4>  
                            <div className="pb-4 pt-3 d-flex flex-row">
                                <i className="material-icons text-serapide icon-34 pr-4 ">assignment</i>
                                <div className="d-flex flex-column ">
                                    <h3 className="mb-0">CREA NUOVO PIANO</h3>
                                    {enti && (<EnteSelector className="pt-5" enti={enti} onChange={selectEnte} isLoading={isLoading} value={ente}></EnteSelector>)}
                                    <span className="pt-4 pb-2 font-weight-bold">Atto di governo del territorio</span>
                                    <span className="pt-2 pb-1small">Seleziona il tipo di atto</span>
                                    <SelectTipo className="mb-5 text-capitolize" onChange={selectTipo} tipiPiano={tipiPiano} value={tipo} isLoading={isLoading}></SelectTipo>
                                    <Button disabled={!canSubmit(ente, isLoading, tipo, isSaving)} onClick={() => creaPiano(getInput(ente, tipo))}
                                        size='md' tag="a" href="./#/nuovo_piano" 
                                        className="mt-5 flex-column d-flex ext-uppercase align-items-center" 
                                        color="serapide" label="CREA PIANO" isLoading={isSaving}>
                                    </Button>
                                </div>   
                            </div>
                        </div>
                        <div className="d-flex flex-column flex-eql "><div className="pb-4 pt-5"><h5 className="text-uppercase">Istruzioni per la compilazione</h5><p>
                        Lore ipsum tante storie queli sono le istruzioni per la compilazione? qui va scritta un botto di roba ma se nessuno
                        mi di ce cosa scrivere non è possibile riempire questo spazio</p>
                        <h5 className="text-uppercase">Dcumenti richiesti per la creazione del piano</h5><p>Lore ipsum tante storie queli sono le istruzioni per la compilazione? qui va scritta un botto di roba ma se nessuno
                        mi di ce cosa scrivere non è possibile riempire questo spazio</p>
                        <h5 className="text-uppercase">Informazioni richieste per la creazione del piano</h5><p>Lore ipsum tante storie queli sono le istruzioni per la compilazione? qui va scritta un botto di roba ma se nessuno
                        mi di ce cosa scrivere non è possibile riempire questo spazio</p></div></div>
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