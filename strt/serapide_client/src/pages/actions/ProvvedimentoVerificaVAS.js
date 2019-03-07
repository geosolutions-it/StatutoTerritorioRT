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
import {Query, Mutation} from 'react-apollo'
import {GET_CONSULTAZIONE_VAS,
    DELETE_RISORSA_CONSULTAZIONE_VAS,
    CONSULTAZIONE_VAS_FILE_UPLOAD
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import  {showError, formatDate} from '../../utils'
import { Label, Input} from 'reactstrap'
const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success

const pareri = [{
    "nome": "Bonifico Caldaia.pdf",
    "uuid": "bc221e59-fec6-4a66-a3c2-1ee95b281426",
    "tipo": "vas_verifica",
    "dimensione": 48.845703125,
    "downloadUrl": "http://127.0.0.1:8000/media/b162fa88-c625-4f53-87b8-e9294dcf7d30/Bonifico_Caldaia.pdf",
    "lastUpdate": "2019-03-06T13:58:13.036686+00:00",
    "user": {
      "fiscalCode": "PPPNDR72D08D512F",
      "firstName": "Alessio",
      "lastName": "Fabiani"
    }
  },
  {
    "nome": "Bollo auto 2018.pdf",
    "uuid": "c7d09ae4-6816-4e50-bca4-72653a7d1cbc",
    "tipo": "vas_semplificata",
    "dimensione": 79.7080078125,
    "downloadUrl": "http://127.0.0.1:8000/media/84b3b1fb-c87f-4fb5-b437-2162c9be21c6/Bollo_auto_2018.pdf",
    "lastUpdate": "2019-03-06T15:22:52.331834+00:00",
    "user": {
      "fiscalCode": "PPPNDR72D08D512F",
      "firstName": "Paolino",
      "lastName": "Paperino"
    }
  }
];
const UI = ({consultazioneSCA: {node: { dataCreazione, dataRicezionePareri, dataScadenza, risorse: {edges=[]} = {}, uuid} = {}} = {}, utente: {fiscalCode} = {}}) => {
    const docPrelim = (edges.filter(({node: {tipo}}) => tipo === "consultazione_vas_preliminare").pop() || {}).node
    const docParere = (edges.filter(({node: {tipo, user = {}}}) => tipo === "consultazione_vas_parere" && fiscalCode === user.fiscalCode).pop() || {}).node
    return (
        <React.Fragment>
            <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Provvedimento di Verifica</h2></div>
            <div className="d-flex mb-3 mt-3 justify-content-between">
                <div className="d-flex">
                    <i className="material-icons text-serapide">check_circle_outline</i>
                    <span className="pl-2">Richiesta Comune</span>
                </div>
                <div>{formatDate(dataCreazione, "dd MMMM yyyy")}</div>
            </div>
            <Resource className="border-0 mt-2" icon="attach_file" resource={docPrelim}></Resource>
            <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                    <i className="material-icons text-serapide pr-3">event_busy</i> 
                    <div className="d-flex flex-column">
                        <span>{formatDate(dataScadenza, "dd MMMM yyyy")}</span>
                        <span>Data entro la quale ricevere i pareri</span>
                    </div>
            </div>
            <div className=" mb-4 border-bottom-2">
            {pareri.map((parere) => (
                <div key={parere.uuid} className="mb-4">
                    <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{parere.user.firstName} {parere.user.lastName}</span></div>
                    <Resource className="border-0 mt-2" icon="attach_file" resource={parere}></Resource>
                </div>
                ))
                }
            </div>
            <h4>Emissione Provvedimento di Verifica</h4> 
            <div className="d-flex mt-3 mb-5 justify-content-around">
                <span className="d-flex justify-content-start pointer">
                    <i className="material-icons text-serapide icon-34">radio_button_checked</i>
                    <span className="pl-2 align-self-center">esclusione da VAS</span>
                </span>
                <span className="d-flex justify-content-start pointer">
                    <i className="material-icons text-serapide icon-34">radio_button_unchecked</i>
                    <span className="pl-2 align-self-center">assoggetamento VAS</span>
                </span>
            </div>
            <h4 className="font-weight-light pl-4 pb-1">PROVVEDIMENTO DI VERIFICA</h4>
                <div style={{width: "100%"}} className="action-uploader d-flex align-self-start pb-5">
                <FileUpload 
                    className="border-0 flex-column"
                    sz="sm" modal={false} showBtn={false} 
                    getSuccess={getSuccess} mutation={CONSULTAZIONE_VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_CONSULTAZIONE_VAS} disabled={false} 
                    isLocked={false} risorsa={undefined} variables={{codice: uuid, tipo: "provvedimento_verifica_vas" }}/>
                </div>
            <div className="align-self-center mt-7">
                <SalvaInvia mutation={CONSULTAZIONE_VAS_FILE_UPLOAD} canCommit={!!docParere}></SalvaInvia>
            </div>
        </React.Fragment>)
    }

    export default ({codicePiano, utente}) => (
        <Query query={GET_CONSULTAZIONE_VAS} variables={{codice: codicePiano}} onError={showError}>
            {({loading, data: {consultazioneVas: {edges = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI consultazioneSCA={edges[0]} utente={utente}/>)}
            }
        </Query>)