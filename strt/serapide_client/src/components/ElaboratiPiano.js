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
import ActionSubParagraphTitle from './ActionSubParagraphTitle'
import {map} from 'lodash'
import {getResourceByType} from 'utils'

const order = ({order: a}, {order: b}) => (a - b)

const getElaborato = (type, resources) => getResourceByType(resources,type)

const getResource = (el, tipo, icon = "picture_as_pdf") => el && (<Resource 
                                    key={tipo}
                                    useLabel
                                    fileSize={false}
                                    className="border-0 mt-3"
                                    icon={icon}
                                    resource={el}/>)

// Due sezioni Elaborati testuali ed elaborati Cartografici
export default ({uuid, tipoPiano ="operativo", resources, mutation, resourceMutation, upload = true, fontSize, iconSize, vertical = false, useLabel = false}) => {
   
    const {testuali = {}} = Elaborati[tipoPiano] || {};
    const {cartografici = {}} = Elaborati[tipoPiano] || {};
    return (
        <React.Fragment>
        <ActionSubParagraphTitle className="size-13 mb-3">Elaborati Testuali</ActionSubParagraphTitle>
        <div className="container border" style={{maxHeight: 200, minHeight: 50, overflowY: "scroll"}}>
            {map(testuali, ((value, tipo) => ({...value, tipo}))).sort(order).map(({label, tooltip, tipo, fileType = "application/pdf"}) => {
                const el = getElaborato(tipo, resources)
                return upload ? (<FileUpload key={tipo}
                    fontSize={fontSize}
                    iconSize={iconSize}
                    vertical={vertical}
                    useLabel={useLabel}
                    mutation={mutation}
                    fileType={fileType}
                    resourceMutation={resourceMutation}
                    placeholder={(<TextTooltip text={label} dataTip={tooltip}/>)}
                    risorsa={el}
                    variables={{codice: uuid, tipo}}
                    className="border-0"
                    disabled={false}
                    isLocked={false}/>) : getResource(el, tipo)
                }
            ) }
        </div>
        <ActionSubParagraphTitle className="size-13 my-3">Elaborati Cartografici</ActionSubParagraphTitle>
        <div className="container border" style={{maxHeight: 200, minHeight: 80, overflowY: "scroll"}}>
            {map(cartografici, ((value, tipo) => ({...value, tipo}))).sort(order).map(({label, tooltip, tipo} ) => {
                const el = getElaborato(tipo, resources)
                return upload ? (<FileUpload key={tipo}
                    mutation={mutation}
                    fontSize={fontSize}
                    iconSize={iconSize}
                    vertical={vertical}
                    useLabel={useLabel}
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
        ) }
        </div>

        </React.Fragment>
)}
