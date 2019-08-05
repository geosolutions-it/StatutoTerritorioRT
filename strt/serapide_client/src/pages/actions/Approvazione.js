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
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import ListaContatti from 'components/ListaContatti'

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
                    resourceMutation: DELETE_RISORSA_APPROVAZIONE, disabled: false, isLocked: false,
                    iconSize: "icon-15", fontSize: "size-11",
                    vertical: true, useLabel: true}
                    
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
                <div className="action-uploader  mt-5 py-1 align-self-start">
                <FileUpload 
                    {...fileProps}
                    placeholder="DELIBERA DI APPROVAZIONE"
                    risorsa={deliberaApprovazione} variables={{codice: uuid, tipo: "delibera_approvazione" }}/>                
                </div>
                <ActionParagraphTitle className="pb-1 d-flex justify-content-between size-14">
                    <span className="my-auto">DATA APPROVAZIONE</span>
                    <EnhancedDateSelector popperPlacement="left" placeholder="SELEZIONA DATA APPROVAZIONE" selected={dataDeliberaApprovazione ? new Date(dataDeliberaApprovazione) : undefined} getInput={getInput(uuid,"dataDeliberaApprovazione")} className="py-0 ml-2 rounded-pill size-8 icon-13" mutation={UPDATE_APPROVAZIONE}/>
                </ActionParagraphTitle>

                
                <ActionParagraphTitle>ELABORATI DEL PIANO</ActionParagraphTitle>
                <Elaborati
                        iconSize="icon-15"
                        fontSize="size-11"
                        vertical
                        useLabel
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={edges}
                        mutation={APPROVAZIONE_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_APPROVAZIONE}
                        uuid={uuid}
                        />
                <ActionParagraphTitle>PUBBLICAZIONE</ActionParagraphTitle> 
                <div className="mt-4 row d-flex align-items-center">
                    <div className="col-2 size-12">URL </div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder="COPIA URL PUBBLICAZIONE" getInput={getInput(uuid, "urlPianoPubblicato")} mutation={UPDATE_APPROVAZIONE} disabled={false}  onChange={undefined} value={urlPianoPubblicato} type="url" />
                    </div>
                </div>
                <div className="w-100 border-top mt-3"></div>
                <ActionParagraphTitle className="pt-4 font-weight-light">DESTINATARI</ActionParagraphTitle>
                <ListaContatti title="SOGGETTI ISTITUZIONALI" contacts={aut}/>
                {/* <h6 className="font-weight-light pb-1 mt-4">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h6>
                <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div> */}
                <div className="w-100 border-top mt-3"></div>
                <div className="align-self-center mt-5">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_APPROVAZIONE} 
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