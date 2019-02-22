/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Button} from 'reactstrap'

export default ({azioni = []}) => (
    <div className="d-flex flex-column pb-4 pt-5">
        <div className="d-flex border-serapide border-top py-5 justify-content-around">
            <span className="d-flex mt-4"><i className="material-icons text-white bg-serapide p-2 mr-2 rounded-circle" style={{borderRadius: 30, fontSize: 44}}>build</i><h2 className="m-0 p-2">STRUMENTI PER LA FORMAZIONE DEL PIANO</h2></span>
        </div>
        <div className="p-5">Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.</div>
        <div className="p-5">
           <div className="d-flex justify-content-around py-5">
                <Button size="lg" color="serapide"><div style={{minWidth: 400}}className="d-flex flex-column"><span>REDAZIONE NORME TECHINCHE</span><span>DI ATTUAZIONE DEL PIANO</span><span>[Minerva]</span></div></Button>
                <Button size="lg" color="serapide"><div style={{minWidth: 400}}className="d-flex flex-column"><span>COMPILAZIONE DEL</span><span>RAPPORTO AMBIENTALE</span><span>[Minerva]</span></div></Button>
           </div>
           <div className="d-flex justify-content-around py-5">
                <Button size="lg" color="serapide"><div style={{minWidth: 400}}className="d-flex flex-column"><span>CONFORMAZIONE</span><span>AL PIT-PPR</span><span>[Crono]</span></div></Button>
                <Button size="lg" color="serapide"><div style={{minWidth: 400}}className="d-flex flex-column"><span>MONITORAGGIO</span><span>URBANISTICO</span><span>[Minerva]</span></div></Button>
           </div>
        </div>
    </div>
)