/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Spinner from 'components/Spinner'
import FileUpload from 'components/UploadSingleFile'

import {rebuildTooltip} from 'enhancers'
import {showError, getCodice, PIANO_DOCS} from 'utils'

import {
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO
} from 'schema'


const UI = rebuildTooltip()(({ back, 
        piano: {risorse : {edges: resources = []} = {}, codice, } = {}, 
        proceduraAvvio: {node: {uuid} = {}} = {},
        fileType = PIANO_DOCS.GENIO
    }) => {
        const [{node: file} = {}] = resources.filter(({node: {tipo}}) => tipo === fileType)
        return (
            <React.Fragment>
                <ActionTitle>Protocollo Genio Civile</ActionTitle>
                <ActionSubParagraphTitle className="size-13 pb-1 pt-5">Carica il documento del protocollo</ActionSubParagraphTitle>
                <div className="action-uploader mt-4 align-self-start border-bottom border-top">
                <FileUpload 
                    iconSize="icon-15"
                    fontSize="size-11"
                    vertical
                    useLabel
                    className="border-0"
                    placeholder={"Documento Protocollo"}
                    disabled={false} 
                    isLocked={false} risorsa={file} variables={{codice, tipo: fileType }}/>
                </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia  fontSize="size-8" tipIconColor="w" onCompleted={back} variables={{codice: uuid}} mutation={INVIO_PROTOCOLLO_GENIO} canCommit={!!file}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges:[proceduraAvvio] = []} = {}} = {}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} proceduraAvvio={proceduraAvvio}/>)}
            }
        </Query>)