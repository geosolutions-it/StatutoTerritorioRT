/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Button} from 'reactstrap'


const goTo = (url) => {
    window.open(url , '_blank');
}

export default ({utente: {attore} = {},
    piano: {redazioneNormeTecnicheAttuazioneUrl, compilazioneRapportoAmbientaleUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl} = {}
    } = {}) => (
    <div className="d-flex flex-column pb-4 pt-5">
        <div className="d-flex border-serapide border-top py-5 justify-content-around">
            <span className="d-flex mt-4 align-items-center" >
                <i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{ fontSize: 44}}>build</i>
                <h2 className="m-0 p-2">STRUMENTI PER LA FORMAZIONE DEL PIANO</h2>
            </span>
        </div>
        <div className="m-auto p-5 text-center" style={{maxWidth: 1000}}>Selezionando uno dei riquadri si accede agli strumenti operativi per la redazione della disciplina del Piano, 
                la valutazione ambientale, la conformazione al PIT-PPR ed il monitoraggio del dimensionamento. del consumo di suolo e del recupero urbano.
        </div>
        <div className="row pt-5">
        
                <div className="col-auto py-2 m-auto">
                    <Button disabled={!redazioneNormeTecnicheAttuazioneUrl} onClick={() => goTo(redazioneNormeTecnicheAttuazioneUrl)}
                            className="margin-auto" style={{minWidth: 344}} size="lg" color="serapide">
                        <div  className="d-flex flex-column">
                            <span>REDAZIONE NORME TECHINCHE</span>
                            <span>DI ATTUAZIONE DEL PIANO</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                        <span>URL</span><div className="border p-2">{redazioneNormeTecnicheAttuazioneUrl}</div>
                    </div>
                </div>
                <div className="col-auto m-auto">
                    <Button disabled={!compilazioneRapportoAmbientaleUrl} onClick={() => goTo( compilazioneRapportoAmbientaleUrl)} 
                            className="margin-auto" style={{minWidth: 344}}  size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>COMPILAZIONE DEL</span>
                            <span>RAPPORTO AMBIENTALE</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2">{compilazioneRapportoAmbientaleUrl}</div>
                    </div>
                </div>
        </div>
        <div className="row">
                <div className="col-auto py-2 m-auto">
                    <Button disabled={!conformazionePitPprUrl} onClick={() => goTo(conformazionePitPprUrl)}
                            className="margin-auto" style={{minWidth: 344}} size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>CONFORMAZIONE</span>
                            <span>AL PIT-PPR</span>
                            <span>[Crono]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2">{conformazionePitPprUrl}</div>
                    </div>
                </div>
                <div className="col-auto m-auto">
                    <Button disabled={!monitoraggioUrbanisticoUrl} onClick={() => goTo(monitoraggioUrbanisticoUrl)}
                            className="margin-auto" style={{minWidth: 344}}  size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>MONITORAGGIO</span>
                            <span>URBANISTICO</span>
                            <span>[Input]</span>
                        </div>
                    </Button>
                    <div className="mt-3 mb-4">
                     <span>URL</span><div className="border p-2">{monitoraggioUrbanisticoUrl}</div>
                    </div>
                </div>
           
        </div>
    </div>
)
