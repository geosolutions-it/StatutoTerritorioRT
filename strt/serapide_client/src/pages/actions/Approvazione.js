/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from "react-apollo"

import FileUpload from 'components/UploadSingleFile'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import TextWithTooltip from 'components/TextWithTooltip'
import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'
import Elaborati from "components/ElaboratiPiano"

import  {showError, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_APPROVAZIONE, UPDATE_APPROVAZIONE,
    DELETE_RISORSA_APPROVAZIONE,
    APPROVAZIONE_FILE_UPLOAD,
    TRASMISSIONE_APPROVAZIONE
} from 'schema'


const getInput = getInputFactory("proceduraApprovazione")

const fileProps = {className: `border-0`, mutation: APPROVAZIONE_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_APPROVAZIONE, disabled: false, isLocked: false}
                    
const UI = rebuildTooltip({onUpdate: false, log: false, comp: "ApprovazioneProc"})(({
    proceduraApprovazione: {
            uuid,
            dataDeliberaApprovazione,
            urlPianoPubblicato,
            risorse: {edges=[]} = {}
            } = {}, 
        piano: {
            tipo: tipoPiano = "",
            autoritaIstituzionali: {edges: aut =[]} = {},
            // altriDestinatari: {edges: dest = []} = {}
            },
        back}) => {

            
            const [{node: deliberaApprovazione} = {}] = edges.filter(({node: {tipo}}) => tipo === "delibera_approvazione")
            
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Approvazione
                </ActionTitle>
                <div className="action-uploader  mt-3 align-self-start ">
                <FileUpload 
                    {...fileProps}
                    placeholder="DELIBERA DI APPROVAZIONE"
                    risorsa={deliberaApprovazione} variables={{codice: uuid, tipo: "delibera_approvazione" }}/>                
                </div>
                <div className="row mt-4">
                    <div className="col-12 d-flex pl-4 align-items-center">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA APPROVAZIONE" selected={dataDeliberaApprovazione ? new Date(dataDeliberaApprovazione) : undefined} getInput={getInput(uuid,"dataDeliberaApprovazione")} className="py-0" mutation={UPDATE_APPROVAZIONE}/></div>
                </div>
                
                <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <Elaborati 
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={edges}
                        mutation={APPROVAZIONE_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_APPROVAZIONE}
                        uuid={uuid}
                        /> 
                <div className="mt-4 row d-flex align-items-center">
                    <div className="col-12">URL PUBBLICAZIONE</div>
                    <div className="col-12 ">
                        <Input placeholder="COPIA URL PUBBLICAZIONE" getInput={getInput(uuid, "urlPianoPubblicato")} mutation={UPDATE_APPROVAZIONE} disabled={false}  onChange={undefined} value={urlPianoPubblicato} type="url" />
                    </div>
                </div>
                <div className="w-100 border-top mt-3"></div>
                <h5 className="pt-4 font-weight-light">DESTINATARI</h5>
                <h6 className="font-weight-light pb-1 mt-2">SOGGETTI ISTITUZIONALI</h6>
                <div className="row">  
                    {aut.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                    </div>
                {/* <h6 className="font-weight-light pb-1 mt-4">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h6>
                <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div> */}
                <div className="w-100 border-top mt-3"></div>
                <div className="align-self-center mt-5">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_APPROVAZIONE} 
                        canCommit={ deliberaApprovazione && dataDeliberaApprovazione  && urlPianoPubblicato}></SalvaInvia>
                </div>
            </React.Fragment>)})

export default (props) => (
                <Query query={GET_APPROVAZIONE} variables={{codice: getCodice(props)}} onError={showError}>
                    {({loading, data: {modello: {edges: [{node: procedura} = {}] = []} = []} = {}}) => {
                        if (loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI {...props} proceduraApprovazione={procedura} />)}
                    }
                </Query>)