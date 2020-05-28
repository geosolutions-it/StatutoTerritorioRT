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
import Spinner from 'components/Spinner'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Resource from 'components/Resource'

import  {showError, getCodice, getResourceByType, VAS_DOCS} from 'utils'

import {GET_ADOZIONE_VAS,
    DELETE_RISORSA_ADOZIONE_VAS,
    ADOZIONE_VAS_FILE_UPLOAD, UPLOAD_ELABORATI_ADOZIONE_VAS
} from 'schema'

const fileProps = { className: `border-0`, mutation: ADOZIONE_VAS_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_ADOZIONE_VAS, disabled: false, isLocked: false,
                    iconSize: "icon-15", fontSize: "size-11",
                    vertical: true, useLabel: true}

const UI = ({
    back,
    vas: { node: {risorse : {edges: resourcesVas = []} = {}} = {}} = {},
    vasAdozione: { node: {uuid, risorse : {edges: resourcesVasAdozione = []} = {}} = {}} = {},
    }) => {
        
        const sintesi = getResourceByType(resourcesVasAdozione, VAS_DOCS.DOCUMENTO_DI_SINTESI)
        const rapporto = getResourceByType(resourcesVas, VAS_DOCS.RAPPORTO_AMBIENTALE)
        const sintesiNon = getResourceByType(resourcesVas, VAS_DOCS.SINTESI_NON_TECNICA)
        return (
            <React.Fragment>
                <ActionTitle>Upload Elaborati VAS</ActionTitle>
                <ActionParagraphTitle>RIFERIMENTI DOCUMENTALI</ActionParagraphTitle>
                <ActionSubParagraphTitle>RAPPORTO AMBIENTALE</ActionSubParagraphTitle>
                <Resource iconSize="icon-15" fontSize="size-11" useLabel fileSize={false} className="border-0 my-3" icon="attach_file" resource={rapporto}/>
                <ActionSubParagraphTitle>SINTESI NON TECNICA</ActionSubParagraphTitle>
                <Resource iconSize="icon-15" fontSize="size-11" useLabel fileSize={false} className="border-0 my-3" icon="attach_file" resource={sintesiNon}/>
                <ActionParagraphTitle>UPLOAD DOCUMENTI</ActionParagraphTitle>
                <ActionSubParagraphTitle>DOCUMENTO DI SINTESI</ActionSubParagraphTitle>
                <div className="action-uploader mt-4 py-1 align-self-start border-bottom">
                <FileUpload 
                    {...fileProps}
                    placeholder="Documento di sintesi"
                    risorsa={sintesi} variables={{codice: uuid, tipo: "documento_sintesi" }}/>
                </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={UPLOAD_ELABORATI_ADOZIONE_VAS} canCommit={sintesi}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default (props) => (
        <Query query={GET_ADOZIONE_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vasAdozione] = []} = {}, modelloVas: {edges:[vas] = []} = {}}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas} vasAdozione={vasAdozione}/>)}
            }
        </Query>)