/*
 * Copyright 2018, GeoSolutions Sas.
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

export default ({utente: {attore} = {}}) => (
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
                    <Button onClick={() => goTo( attore === "Comune" ? "http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" : "http://159.213.57.114/vas046021/gotoP/RegioneToscana/14042017/PS191218")}
                            className="margin-auto" style={{minWidth: 344}} size="lg" color="serapide">
                        <div  className="d-flex flex-column">
                            <span>REDAZIONE NORME TECHINCHE</span>
                            <span>DI ATTUAZIONE DEL PIANO</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                </div>
                <div className="col-auto m-auto">
                    <Button onClick={() => goTo( attore === "Comune" ? "http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" : "http://159.213.57.114/vas046021/gotoP/RegioneToscana/14042017/PS191218")} 
                            className="margin-auto" style={{minWidth: 344}}  size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>COMPILAZIONE DEL</span>
                            <span>RAPPORTO AMBIENTALE</span>
                            <span>[Minerva]</span>
                        </div>
                    </Button>
                </div>
        </div>
        <div className="row">
                <div className="col-auto py-2 m-auto">
                    <Button onClick={() => goTo(attore === "Comune" ? "http://159.213.57.114/crono046021/gotoP/046021/07062018/PS191218" : "http://159.213.57.114/crono046021/gotoP/RegioneToscana/14042017/PS191218")}
                            className="margin-auto" style={{minWidth: 344}} size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>CONFORMAZIONE</span>
                            <span>AL PIT-PPR</span>
                            <span>[Crono]</span>
                        </div>
                    </Button>
                </div>
                <div className="col-auto m-auto">
                    <Button onClick={() => goTo("http://159.213.57.114/Database%20Strumenti%20Urbanistici.html")}
                            className="margin-auto" style={{minWidth: 344}}  size="lg" color="serapide">
                        <div className="d-flex flex-column">
                            <span>MONITORAGGIO</span>
                            <span>URBANISTICO</span>
                            <span>[Input]</span>
                        </div>
                        
                    </Button>
                </div>
           
        </div>
    </div>
)