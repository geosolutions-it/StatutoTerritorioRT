/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from './UploadSingleFile'
import {map} from "lodash"
import Elaborati from "../Elaborati"
import TextTooltip from "./TextWithTooltip"
import {rebuildTooltip} from "../enhancers/utils"
const getElaborato = (type, resources) => resources.filter( ({node: {tipo}}) => tipo === type).map(({node}) => (node)).shift()


// Due sezioni Elaborati testuali ed elaborati Cartografici
export default ({uuid, tipoPiano ="operativo", resources, mutation, resourceMutation}) => {

    return (
        <React.Fragment>
        <h6 className="mt-3 font-weight-light">Elaborati Testuali</h6>
        <div className="container border" style={{height: 200, overflowY: "scroll"}}>
            {map((Elaborati[tipoPiano] && Elaborati[tipoPiano]["testuali"]) || [], (({label, tooltip}, tipo) => (
                <FileUpload key={tipo}
                    mutation={mutation}
                    resourceMutation={resourceMutation}
                    placeholder={(<TextTooltip text={label} dataTip={tooltip}/>)}
                    risorsa={getElaborato(tipo, resources)}
                    variables={{codice: uuid, tipo}}
                    className="border-0"
                    disabled={false}
                    isLocked={false}/>
            ))) }
        </div>
        <h6 className="mt-3 font-weight-light">Elaborati Cartografici</h6>
        <div className="container border" style={{height: 200, overflowY: "scroll"}}>
            {map((Elaborati[tipoPiano] && Elaborati[tipoPiano]["cartografici"]) || [], (({label, tooltip}, tipo) => (
                <FileUpload key={tipo}
                    mutation={mutation}
                    resIcon="map"
                    fileType="application/zip,application/x-zip-compressed,.zip"
                    resourceMutation={resourceMutation}
                    placeholder={(<TextTooltip text={label} dataTip={tooltip}/>)}
                    risorsa={getElaborato(tipo, resources)}
                    variables={{codice: uuid, tipo}}
                    className="border-0"
                    disabled={false}
                    isLocked={false}/>
            ))) }
        </div>

        </React.Fragment>
)}
