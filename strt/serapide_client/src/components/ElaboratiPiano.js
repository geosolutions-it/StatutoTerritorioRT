/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import FileUpload from './UploadSingleFile'
import Elaborati from "../Elaborati"
import TextTooltip from "./TextWithTooltip"
import Resource from './Resource'

import {map} from "lodash"

const getElaborato = (type, resources) => resources.filter( ({node: {tipo}}) => tipo === type).map(({node}) => (node)).shift()

const getResource = (el, tipo, icon = "picture_as_pdf") => el && (<Resource 
                                    key={tipo}
                                    useLabel
                                    fileSize={false}
                                    className="border-0 mt-3"
                                    icon={icon}
                                    resource={el}/>)
// Due sezioni Elaborati testuali ed elaborati Cartografici
export default ({uuid, tipoPiano ="operativo", resources, mutation, resourceMutation, upload = true}) => {

    return (
        <React.Fragment>
        <h6 className="mt-3 font-weight-light">Elaborati Testuali</h6>
        <div className="container border" style={{maxHeight: 200, minHeight: 50, overflowY: "scroll"}}>
            {map((Elaborati[tipoPiano] && Elaborati[tipoPiano]["testuali"]) || [], (({label, tooltip}, tipo) => {
                const el = getElaborato(tipo, resources)
                return upload ? (<FileUpload key={tipo}
                    mutation={mutation}
                    resourceMutation={resourceMutation}
                    placeholder={(<TextTooltip text={label} dataTip={tooltip}/>)}
                    risorsa={el}
                    variables={{codice: uuid, tipo}}
                    className="border-0"
                    disabled={false}
                    isLocked={false}/>) : getResource(el, tipo)
                }
            )) }
        </div>
        <h6 className="mt-3 font-weight-light">Elaborati Cartografici</h6>
        <div className="container border" style={{maxHeight: 200, minHeight: 80, overflowY: "scroll"}}>
            {map((Elaborati[tipoPiano] && Elaborati[tipoPiano]["cartografici"]) || [], (({label, tooltip}, tipo) => {
                const el = getElaborato(tipo, resources)
                    
                return upload ? (<FileUpload key={tipo}
                    mutation={mutation}
                    resIcon="map"
                    fileType="application/zip,application/x-zip-compressed,.zip"
                    resourceMutation={resourceMutation}
                    placeholder={(<TextTooltip text={label} dataTip={tooltip}/>)}
                    risorsa={getElaborato(tipo, resources)}
                    variables={{codice: uuid, tipo}}
                    className="border-0"
                    disabled={false}
                    isLocked={false}/>) : getResource(el, tipo, "map")
            }
        )) }
        </div>

        </React.Fragment>
)}
