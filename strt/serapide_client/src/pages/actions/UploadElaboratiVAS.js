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
import {Query} from 'react-apollo'
import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD, UPLOAD_ELABORATI_VAS
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'

import  {showError} from '../../utils'


const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}}
    }) => {
        
        const elaborati =  resources.filter(({node: {tipo, user = {}}}) => tipo === 'elaborati_vas').map(({node}) => node)
        const rapporto = resources.filter(({node: {tipo, user = {}}}) => tipo === 'rapporto_ambientale').map(({node}) => node).shift()
        
        return (
            <React.Fragment>
                <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Upload Elaborati VAS</h2></div>
                <p>Il comune esamina i pareri, forma il piano e redige il Rapporto Ambientale. Gli elaborati vengono caricati nella piattafo</p>
                <div className="action-uploader mt-3 align-self-start border-bottom border-top mb-3">
                <FileUpload 
                    className="border-0"
                    placeholder="Rapporto Ambientale"
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>
                <h4 className="font-weight-light pl-4 pb-1">Elaborati</h4>
                <UploadFiles risorse={elaborati} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS}
                        variables={{codice: uuid, tipo: "elaborati_vas" }}
                        isLocked={false} getSuccess={({uploadRisorsaVas: {success}}) => success} getFileName={({uploadRisorsaVas: {fileName} = {}}) => fileName}/>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{uuid}} mutation={UPLOAD_ELABORATI_VAS} canCommit={rapporto && elaborati.length > 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({codicePiano, utente, scadenza, back, tipo, label, tipoVas, saveMutation}) => (
        <Query query={GET_VAS} variables={{codice: codicePiano}} onError={showError}>
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
                    <UI back={back} vas={edges[0]} utente={utente} tipoVas={tipoVas} saveMutation={saveMutation} scadenza={scadenza} tipoDoc={tipo} label={label}/>)}
            }
        </Query>)