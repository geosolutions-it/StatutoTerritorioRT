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

import  {showError, getCodice} from 'utils'

import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD, REDAZIONE_DOCUMENTI_VAS
} from 'schema'

const UI = ({
    back,
    // piano: {tipo: tipoPiano} = {}, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {}
    }) => {
        
        const rapporto = resources.filter(({node: {tipo, user = {}}}) => tipo === 'rapporto_ambientale').map(({node}) => node).shift()
        const sintesi = resources.filter(({node: {tipo, user = {}}}) => tipo === 'sintesi_non_tecnica').map(({node}) => node).shift()
        return (
            <React.Fragment>
                <ActionTitle>Redazione Elaborati VAS</ActionTitle>
                <div className="d-flex pt-2 mb-5 size-13 text-justify">Il comune esamina i pareri, redige il Rapporto Ambientale e la Sintesi non tecnica. Gli elaborati vengono caricati nella piattaforma</div>
                <div className="action-uploader  py-1 align-self-start border-bottom  border-top">
                <FileUpload 
                    iconSize="icon-15" fontSize="size-11"
                    vertical useLabel
                    className="border-0"
                    placeholder="Rapporto ambientale"
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>
                <div className="action-uploader  py-1 align-self-start border-bottom">
                <FileUpload 
                    iconSize="icon-15" fontSize="size-11"
                    vertical useLabel
                    className="border-0"
                    placeholder="Documento di sintesi non tecnica"
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={sintesi} variables={{codice: uuid, tipo: "sintesi_non_tecnica" }}/>
                </div>
                {/* <h4 className="font-weight-light pl-4 pb-1">Elaborati</h4>
                <Elaborati
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={resources}
                        mutation={VAS_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_VAS}
                        uuid={uuid}
                /> */}
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{uuid}} mutation={REDAZIONE_DOCUMENTI_VAS} canCommit={rapporto && sintesi}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default 
    (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas}/>)}
            }
        </Query>)