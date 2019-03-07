/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Input} from 'reactstrap'
import Resource from '../../components/Resource'
import {Query, Mutation} from 'react-apollo'
import {GET_CONSULTAZIONE_VAS,
    CONSULTAZIONE_VAS_FILE_UPLOAD
} from '../../queries'
import SalvaInvia from '../../components/SalvaInvia'
import  {showError, formatDate} from '../../utils'

const getSuccess = ({uploadConsultazioneVas: {success}} = {}) => success


const UI = ({consultazioneSCA: {node: { dataCreazione, dataRicezionePareri, dataScadenza, risorse: {edges=[]} = {}, uuid} = {}} = {}, utente: {fiscalCode} = {}}) => {
    const docPrelim = (edges.filter(({node: {tipo}}) => tipo === "consultazione_vas_preliminare").pop() || {}).node
    const docParere = (edges.filter(({node: {tipo, user = {}}}) => tipo === "consultazione_vas_parere" && fiscalCode === user.fiscalCode).pop() || {}).node
    return (
        <React.Fragment>
            <div  className="py-3 border-bottom-2 border-top-2"><h2 className="m-0">Pubblicazione Provvedimento di Verifica</h2></div>
            <Resource className="border-0 mt-2" icon="attach_file" resource={docPrelim}></Resource>
            
            <span style={{maxWidth: 400}} className="mt-5 d-flex align-items-center">
                <i className="material-icons icon34 text-serapide">link</i>
                <Input disabled={false}  type="url" name="text" />
            </span>
            <span style={{fontSize: "80%", maxWidth: 400}}className="pl-4 font-80">Inserire la URL della pagina dove è stato pubblicato il provvedimento di verifica</span>
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