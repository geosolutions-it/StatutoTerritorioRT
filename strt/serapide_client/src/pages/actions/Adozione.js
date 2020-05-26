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
import Resource from 'components/Resource'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Spinner from 'components/Spinner'

import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'
import Elaborati from 'components/ElaboratiPiano'
import {List as Si} from 'components/SoggettiIstituzionali'

import  {showError, getResourceByType, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE, UPDATE_ADOZIONE,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD,
    TRASMISSIONE_ADOZIONE,
    UPDATE_PIANO
} from 'schema'

 

const getInput = getInputFactory("proceduraAdozione")
const getInputPiano = (codice, field) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: { [field]:  val }, 
            codice
        }
    }
})

const fileProps = {className: `border-0`, mutation: ADOZIONE_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_ADOZIONE, disabled: false, isLocked: false,
                    iconSize: "icon-15", fontSize: "size-11",
                    vertical: true, useLabel: true}
                    
const UI = rebuildTooltip({onUpdate: false, log: false, comp: "AdozioneProc"})(({
    vas: {node:{ risorse: {edges: resVas =[]} = {}} = {}} = {},
    proceduraAdozione: {node: {
            uuid,
            dataDeliberaAdozione, dataRicezioneOsservazioni,
            dataRicezionePareri,
            risorse: {edges=[]} = {}
            } = {}} = {}, 
        piano: {
            codice,
            tipo: tipoPiano = "",
            redazioneNormeTecnicheAttuazioneUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl,
            compilazioneRapportoAmbientaleUrl,
            soggettiOperanti,
            risorse: {edges: resources=[]} = {}
            
            },
        back}) => {

            
            const deliberaAdozione = getResourceByType(edges, "delibera_adozione")
            const norme = getResourceByType(resources, "norme_tecniche_attuazione")
            
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Adozione
                </ActionTitle>
                <ActionParagraphTitle>RIFERIMENTI DOCUMENTALI</ActionParagraphTitle>
                <ActionSubParagraphTitle>NORME TECNICHE DI ATTUAZIONE</ActionSubParagraphTitle>
                <Resource iconSize="icon-15" fontSize="size-11" useLabel fileSize={false} className="border-0 my-3" icon="attach_file" resource={norme}/>
                <ActionSubParagraphTitle>COMPILAZIONE RAPPORTO AMBIENTALE</ActionSubParagraphTitle>
                <div className="my-3 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10"  placeholder="copiare la URL in questo campo" getInput={getInputPiano(codice, "compilazioneRapportoAmbientaleUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={compilazioneRapportoAmbientaleUrl} type="text" />
                    </div>
                </div>
                <ActionSubParagraphTitle>CONFORMAZIONE AL PIT-PPR</ActionSubParagraphTitle>
                <div className="my-3 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10" placeholder="copiare la URL in questo campo" getInput={getInputPiano(codice, "conformazionePitPprUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={conformazionePitPprUrl} type="text" />
                    </div>
                </div>
                <ActionSubParagraphTitle>MONITORAGGIO URBANISTICA</ActionSubParagraphTitle>
                <div className="my-3 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10" placeholder="copiare la URL in questo campo" getInput={getInputPiano(codice, "monitoraggioUrbanisticoUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={monitoraggioUrbanisticoUrl} type="text" />
                    </div>
                </div>
                <div className="w-100 border-top m-0 mt-4"></div>
                <ActionSubParagraphTitle className="pt-4 font-weight-light">DESTINATARI</ActionSubParagraphTitle>
                <Si soggettiOperanti={soggettiOperanti}/>
                <div className="w-100 border-top mt-3"></div>
                <div className="action-uploader  mt-5 py-1 align-self-start border-bottom">
                <FileUpload 
                    {...fileProps}
                    placeholder="DELIBERA DI ADOZIONE"
                    risorsa={deliberaAdozione} variables={{codice: uuid, tipo: "delibera_adozione" }}/>                
                </div>

                <ActionParagraphTitle className="pb-1 d-flex justify-content-between size-14">
                    <span className="my-auto">DATA ADOZIONE</span>
                    <EnhancedDateSelector popperPlacement="left" placeholder="SELEZIONA DATA ADOZIONE" selected={dataDeliberaAdozione ? new Date(dataDeliberaAdozione) : undefined} getInput={getInput(uuid,"dataDeliberaAdozione")} className="py-0 ml-2 rounded-pill size-8 icon-13" mutation={UPDATE_ADOZIONE}/>
                </ActionParagraphTitle>
                
                <ActionParagraphTitle>ELABORATI DEL PIANO</ActionParagraphTitle>
                <Elaborati
                        iconSize="icon-15"
                        fontSize="size-11"
                        vertical
                        useLabel
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={edges}
                        mutation={ADOZIONE_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        uuid={uuid}
                        />               
                <div className="w-100 border-top mt-3"></div>                
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_ADOZIONE} 
                        canCommit={ deliberaAdozione && dataDeliberaAdozione && compilazioneRapportoAmbientaleUrl && conformazionePitPprUrl && monitoraggioUrbanisticoUrl}></SalvaInvia>
                </div>
            </React.Fragment>)})

export default (props) => {
    const codice = getCodice(props)
    return (
        <Query query={GET_ADOZIONE} variables={{codice}} onError={showError}>
            {({loading, data: { modello: {edges: [proceduraAdozione] = []} = {}, modelloVas: {edges: [vas] = []} = {}} = {} }) => {
                return loading ? <Spinner/> : <UI {...props} vas={vas} proceduraAdozione={proceduraAdozione} />
                }
            }
        </Query>)
    }
        