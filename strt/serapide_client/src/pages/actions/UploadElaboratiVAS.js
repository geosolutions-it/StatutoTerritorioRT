/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import UploadFiles from '../../components/UploadFiles'
import FileUpload from '../../components/UploadSingleFile'
import ActionTitle from '../../components/ActionTitle'
import {Query} from 'react-apollo'
import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD, UPLOAD_ELABORATI_VAS
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'

import  {showError} from '../../utils'


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}}
    }) => {
        
        const elaborati =  resources.filter(({node: {tipo, user = {}}}) => tipo === 'elaborati_vas').map(({node}) => node)
        const rapporto = resources.filter(({node: {tipo, user = {}}}) => tipo === 'rapporto_ambientale').map(({node}) => node).shift()
        
        return (
            <React.Fragment>
                <ActionTitle>Upload Elaborati VAS</ActionTitle>
                <p>Il comune esamina i pareri, forma il piano e redige il Rapporto Ambientale. Gli elaborati vengono caricati nella piattafo</p>
                <div className="action-uploader mt-3 align-self-start border-bottom border-top mb-3">
                <FileUpload 
                    className="border-0"
                    placeholder="Documento preliminare di VAS"
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">Elaborati</h4>
                <UploadFiles risorse={elaborati} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS}
                        variables={{codice: uuid, tipo: "elaborati_vas" }}
                        isLocked={false} />
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{uuid}} mutation={UPLOAD_ELABORATI_VAS} canCommit={rapporto && elaborati.length > 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {}, back}) => (
        <Query query={GET_VAS} variables={{codice: piano.codice}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} vas={edges[0]}/>)}
            }
        </Query>)