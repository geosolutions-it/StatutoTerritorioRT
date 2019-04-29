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
// import Elaborati from 'components/ElaboratiPiano'

import  {showError, getCodice} from 'utils'

import {GET_ADOZIONE_VAS,
    DELETE_RISORSA_ADOZIONE_VAS,
    ADOZIONE_VAS_FILE_UPLOAD, UPLOAD_ELABORATI_ADOZIONE_VAS
} from 'schema'

const UI = ({
    back,
    // piano: {tipo: tipoPiano} = {}, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {}
    }) => {
        
        const [{node: sintesi} = {}] = resources.filter(({node: {tipo}}) => tipo === 'documento_sintesi')
        const [{node: rapporto} = {}] = resources.filter(({node: {tipo}}) => tipo === 'rapporto_ambientale')
    // const elaboratiCompleti = elaboratiCompletati(tipoPiano, resources)
        return (
            <React.Fragment>
                <ActionTitle>Upload Elaborati VAS</ActionTitle>
                
                <div className="action-uploader mt-3 align-self-start border-bottom border-top mb-3">
                <FileUpload 
                    className="border-0"
                    placeholder="Documento di sintesi"
                    mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_ADOZIONE_VAS} disabled={false} 
                    isLocked={false} risorsa={sintesi} variables={{codice: uuid, tipo: "documento_sintesi" }}/>
                </div>
                <div className="action-uploader mt-3 align-self-start border-bottom border-top mb-3">
                <FileUpload 
                    className="border-0"
                    placeholder="Rapporto ambientale"
                    mutation={ADOZIONE_VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_ADOZIONE_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>
                {/* <h4 className="font-weight-light pl-4 pb-1">Elaborati</h4>
                <Elaborati
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={resources}
                        mutation={ADOZIONE_VAS_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_ADOZIONE_VAS}
                        uuid={uuid}
                /> */}
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={UPLOAD_ELABORATI_ADOZIONE_VAS} canCommit={rapporto && sintesi}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default (props) => (
        <Query query={GET_ADOZIONE_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} vas={vas}/>)}
            }
        </Query>)