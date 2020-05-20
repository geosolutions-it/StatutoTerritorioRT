/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import FileUpload from 'components/UploadSingleFile'
import ActionTitle from 'components/ActionTitle'
import SalvaInvia from 'components/SalvaInvia'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Spinner from 'components/Spinner'


import  {showError, getCodice} from 'utils'


export const UI = ({
    back,
    fileType = 'rapporto_ambientale',
    title = "Upload file",
    subTitle,
    closeAction,
    placeholder = "Documento",
    uploadRes,
    deleteRes,
    // piano: {tipo: tipoPiano} = {}, 
    modello: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    children,
    canCommit = true
    }) => {
        
        const [{node: file} = {}] = resources.filter(({node: {tipo, user = {}}}) => tipo === fileType)
        
        return (
            <React.Fragment>
                <ActionTitle>{title}</ActionTitle>
                <ActionSubParagraphTitle className="size-13 pb-1 pt-5">{subTitle}</ActionSubParagraphTitle>
                <div className="action-uploader mt-4 align-self-start border-bottom border-top">
                <FileUpload 
                    iconSize="icon-15"
                    fontSize="size-11"
                    vertical
                    useLabel
                    className="border-0"
                    placeholder={placeholder}
                    mutation={uploadRes} 
                    resourceMutation={deleteRes} disabled={false} 
                    isLocked={false} risorsa={file} variables={{codice: uuid, tipo: fileType }}/>
                </div>
                {children && children}
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={closeAction} canCommit={canCommit && file}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({query, ...props}) => (
        <Query query={query} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [modello] = []} = {}}}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} modello={modello}/>)}
            }
        </Query>)