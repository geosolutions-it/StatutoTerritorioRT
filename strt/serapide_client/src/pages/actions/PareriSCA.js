/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import Resource from '../../components/Resource'
import { VAS_FILE_UPLOAD, DELETE_RISORSA_VAS} from '../../queries'
import Button from '../../components/IconButton'
import Switch from '../../components/Switch'

const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success

export default () => {
    return (
        <React.Fragment>
            <div  className="mt-3 py-3 border-bottom-2 border-top-2"><h2 className="m-0">Pareri SCA</h2></div>
            <div className="d-flex mb-3 mt-3 justify-content-between">
                <div className="d-flex">
                    <i className="material-icons text-serapide">check_circle_outline</i>
                    <span className="pl-2">Richiesta Comune</span>
                </div>
                <div>22/10/2019</div>
            </div>
            <Resource className="border-0 mt-2" icon="attach_file" resource={{nome: "documento_preliminare.pdf"}}></Resource>
            <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                    <i className="material-icons text-serapide pr-3">event_busy</i> 
                    <div className="d-flex flex-column">
                        <span>22/10/2019</span>
                        <span>Data entro la quale ricevere i pareri</span>
                    </div>
            </div>
            <h4 className="font-weight-light pl-4 pb-1">Parere</h4>
            <div className="align-self-start pb-5">
            <FileUpload 
                className="border-0"
                sz="sm" modal={false} showBtn={false} 
                getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                isLocked={false} risorsa={undefined} variables={{codice: "pino", tipo: "vas_verifica" }}/>
            </div>
            
            <div className="align-self-center mt-5">
            <Button isLoading={false} onClick={() => {}} className=" text-uppercase" disabled={false} color="serapide"  label="SALVA ED INVIA"></Button>
            </div>
        </React.Fragment>)
    }