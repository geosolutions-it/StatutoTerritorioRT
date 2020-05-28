/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Button} from 'reactstrap'
import {Query} from "react-apollo"; 

import {GET_VAS} from 'schema'
import PianoPageContainer from 'components/PianoPageContainer';
import PianoSubPageTitle from 'components/PianoSubPageTitle';
import Spinner from 'components/Spinner'

import {AVVIO_DOCS, getResourceByType, VAS_DOCS, getCodice, showError} from 'utils'

const goTo = (url) => {
    window.open(url , '_blank');
}

export const UI = ({
    piano: {
        compilazioneRapportoAmbientaleUrl,
        conformazionePitPprUrl,
        monitoraggioUrbanisticoUrl,
        risorse: {edges: resources = []}} = {},
    vas: {risorse: {edges: resourcesVAS = []} = {}} = {}
    } = {}) => { 
        const norme = getResourceByType(resources, AVVIO_DOCS.NORME_TECNICHE_ATTUAZIONE)
        const urlNorme = norme?.downloadUrl
        const ra = getResourceByType(resourcesVAS, VAS_DOCS.RAPPORTO_AMBIENTALE)
        const urlRa = ra?.downloadUrl
    return (
       <PianoPageContainer>
           <PianoSubPageTitle icon="build" title="STRUMENTI PER LA FORMAZIONE DEL PIANO"/>
           
        <div className="m-auto p-5 text-center" style={{maxWidth: 1000}}>Selezionando uno dei riquadri si accede agli strumenti operativi per la redazione della disciplina del Piano, 
                la valutazione ambientale, la conformazione al PIT-PPR ed il monitoraggio del dimensionamento. del consumo di suolo e del recupero urbano.
        </div>
        <div className="row pt-5">
        
                <div className="col-auto d-flex flex-column py-2 m-auto">
                    <Button disabled={!urlNorme} onClick={() => goTo(urlNorme)}
                            className="margin-auto align-self-center" style={{minWidth: "20rem", maxWidth:"20rem"}} size="lg" color="serapide">
                        <div  className="d-flex flex-column size-16">
                            <span>REDAZIONE DISCIPLINA</span>
                            <span>DEL PIANO</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                        <span>URL</span><div className="border p-2 overflow-hidden size-12" style={{width: "25rem", textOverflow: "ellipsis"}}>{urlNorme}</div>
                    </div>
                </div>
                <div className="col-auto d-flex flex-column m-auto">
                    <Button disabled={!urlRa} onClick={() => goTo(urlRa)} 
                            className="margin-auto align-self-center" style={{minWidth: "20rem", maxWidth:"20rem"}}  size="lg" color="serapide">
                        <div className="d-flex flex-column size-16">
                            <span>VALUTAZIONE E MONITORAGGIO</span>
                            <span>DEGLI EFFETTI AMBIENTALI</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2 overflow-hidden size-12" style={{width: "25rem", textOverflow: "ellipsis"}}>{urlRa}</div>
                    </div>
                </div>
        </div>
        <div className="row">
                <div className="col-auto d-flex flex-column py-2 m-auto">
                    <Button disabled={!conformazionePitPprUrl} onClick={() => goTo(conformazionePitPprUrl)}
                            className="margin-auto align-self-center" style={{minWidth: "20rem", maxWidth:"20rem"}} size="lg" color="serapide">
                        <div className="d-flex flex-column size-16">
                            <span>CONFORMAZIONE</span>
                            <span>AL PIT-PPR</span>
                            <span>[Crono]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2 overflow-hidden size-12" style={{width: "25rem", textOverflow: "ellipsis"}}>{conformazionePitPprUrl}</div>
                    </div>
                </div>
                <div className="col-auto d-flex flex-column m-auto">
                    <Button disabled={!monitoraggioUrbanisticoUrl} onClick={() => goTo(monitoraggioUrbanisticoUrl)}
                            className="margin-auto align-self-center" style={{minWidth: "20rem", maxWidth:"20rem"}}  size="lg" color="serapide">
                        <div className="d-flex flex-column size-16">
                            <span>MONITORAGGIO</span>
                            <span>URBANISTICO</span>
                            <span>[Input]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2 overflow-hidden size-12" style={{width: "25rem", textOverflow: "ellipsis"}}>{monitoraggioUrbanisticoUrl}</div>
                    </div>
                </div>
           
        </div>
    </PianoPageContainer> 
)}



export default (props) => (
    <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [{node: vas} = {}]= []} = {}} = {}}) => {
                return loading ? <Spinner/> : <UI {...props} vas={vas} />
            }}
        </Query>)