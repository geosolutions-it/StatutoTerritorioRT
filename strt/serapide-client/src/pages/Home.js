/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import NavBar from '../components/NavigationBar'
import Button from '../components/IconButton'
export default (props) => {
    return (
        <div className="App">
            <NavBar/>
            <div id="serapide_content" className="pt-5 pX-md px-1 serapide-top-offset position-relative">
            <h1>Portale del territorio</h1>
            <h2>Strumenti per la formazione e gestione dei piani</h2>
            <hr className="border-warning border-bottom"></hr>
            <div className="pt-4 d-flex flex-row flex-wrap">
                <div className="d-flex flex-column ">
                    <h2>Virgina Nardi</h2>
                    <p>Comune di Scandicci</p>
                </div>
                <Button tag="a" href="./#/nuovo_piano" className="ml-auto my-auto text-uppercase" color="warning" icon="note_add" label="Crea nuovo piano"></Button>
                <div className="px-sm-4"></div>
                <Button tag="a" href="./#/archivio" className="my-auto text-uppercase" color="warning" icon="view_list" label="archivio piani"></Button>
            
            </div>
            </div>
        </div>)
    }