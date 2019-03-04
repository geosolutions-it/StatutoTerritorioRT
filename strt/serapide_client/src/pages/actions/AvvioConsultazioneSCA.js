/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import { toast } from 'react-toastify'
import { VAS_FILE_UPLOAD, DELETE_RISORSA_VAS} from '../../queries'
import Button from '../../components/IconButton'
import Switch from '../../components/Switch'

import {Query} from "react-apollo"

const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success
const getVasTypeInput = (uuid) => (tipologia) => ({
    variables: {
        input: { 
            proceduraVas: {
            tipologia}, 
        uuid}
    }
})
const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid}}) => ({label: nome, value: uuid}))
}

const showError = (error) => {
    toast.error(error.message,  {autoClose: true})
}
export default () => {
    return (
        <React.Fragment>
            <div  className="mt-5"><h2 className="m-0">Avvio Consultazioni SCA</h2></div>
            <div className="d-flex py-3 my-4 justify-content-between border-bottom-2 border-top-2">
                <div className="d-flex">
                    <i className="material-icons text-serapide">check_circle_outline</i>
                    <span className="pl-2">Richiesta Comune</span>
                </div>
                <div>22/10/2019</div>
            </div>
            
            <h4 className="mt-2 font-weight-light">DOCUMENTO PRELIMINARE</h4>
            <div className="align-self-start pb-5">
            <FileUpload 
                className="border-0"
                sz="sm" modal={false} showBtn={false} 
                getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                isLocked={false} risorsa={undefined} variables={{codice: "pino", tipo: "vas_verifica" }}/>
            </div>
            
                <div className="d-flex justify-content-between">
                    <div className="d-flex flex-column">
                        <div className="d-flex pb-3"> <i className="material-icons text-serapide pr-3">email</i> <Switch label="Avvia consultazione SCA"/> </div>
                        <span style={{maxWidth: 500}}>Selezionando l’opzione e cliccando “Salva e Invia” verrà inviata comunicazione e
                        documento preliminare agli SCA selezionati e per conoscenza all’Autorità Competente
                        in materia ambientale identificati all’atto di creazione del Piano.</span>
                    </div>
                    <div className="d-flex">
                    <i className="material-icons pr-3">event_busy</i> 
                    <div className="d-flex flex-column">
                        <span>22/10/2019</span>
                        <span style={{maxWidth: 150}}>90 giorni per ricevere i pareri sca</span>
                    </div>
                    </div>
                
                </div>


            <div className="align-self-center mt-5">
            <Button isLoading={false} onClick={() => {}} className=" text-uppercase" disabled={false} color="serapide"  label="SALVA ED INVIA"></Button>
            </div>
        </React.Fragment>)
    }