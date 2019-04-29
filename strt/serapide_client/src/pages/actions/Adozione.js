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
import TextWithTooltip from 'components/TextWithTooltip'
import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'
import Elaborati from "components/ElaboratiPiano"

import  {showError, formatDate, elaboratiCompletati, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE, UPDATE_ADOZIONE, GET_VAS,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD,
    TRASMISSIONE_ADOZIONE
} from 'schema'


const getInput = getInputFactory("proceduraAdozione")

const fileProps = {className: `border-0`, mutation: ADOZIONE_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_ADOZIONE, disabled: false, isLocked: false}
                    
const UI = rebuildTooltip({onUpdate: false, log: false, comp: "AdozioneProc"})(({
    vas: {node:{ risorse: {edges: resVas =[]} = {}} = {}} = {},
    proceduraAdozione: {node: {
            uuid,
            dataDeliberaAdozione, dataRicezioneOsservazioni,
            dataRicezionePareri, pubblicazioneBurtUrl,
            pubblicazioneBurtData, pubblicazioneSitoUrl,
            pubblicazioneSitoData,
            risorse: {edges=[]} = {}
            } = {}} = {}, 
        piano: {
            tipo: tipoPiano = "",
            redazioneNormeTecnicheAttuazioneUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl,
            autoritaIstituzionali: {edges: aut =[]} = {},
            altriDestinatari: {edges: dest = []} = {}
            },
        back}) => {

            const {node: rapportoAmbientale} = resVas.filter(({node: {tipo}}) => tipo === "rapporto_ambientale").shift() || {}
            const {node: deliberaAdozione} = edges.filter(({node: {tipo}}) => tipo === "delibera_adozione").shift() || {}
            const elaboratiCompleti = elaboratiCompletati(tipoPiano, edges)
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Adozione
                </ActionTitle>
                <h5 className="pt-5 font-weight-light">RIFERIMENTI DOCUMENTALI</h5>
                <h6 className="pt-3 font-weight-light">NORME TECHINICHE DI ATTUAZIONE E RAPPORTO AMBIENTALE</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={redazioneNormeTecnicheAttuazioneUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{redazioneNormeTecnicheAttuazioneUrl}</a>
                    </div>
                </div>
                <Resource useLabel fileSize={false} className="border-0 mt-3" icon="attach_file" resource={rapportoAmbientale}/>
                <h6 className="pt-3 font-weight-light">CONFORMAZIONE AL PIT-PPR</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={conformazionePitPprUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{conformazionePitPprUrl}</a>
                    </div>
                </div>
                <h6 className="pt-3 font-weight-light">MONITORAGGIO URBANISTICO</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={monitoraggioUrbanisticoUrl} target="_blank" rel="noopener noreferrer" className="pl-1 text-secondary">{monitoraggioUrbanisticoUrl}</a>
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
                <h6 className="font-weight-light pb-1 mt-4">ALTRI DESTINATARI<TextWithTooltip dataTip="art.8 co.1 L.R. 65/2014"/></h6>
                <div className="row">
                            {dest.map(({node: {nome, uuid} = {}}) => (<div className="col-sm-12 col-md-5 col-lg-4 col-xl-3 d-flex my-1" key={uuid}>
                                    <i className="material-icons text-serapide">bookmark</i>
                                    {nome}
                            </div>))}
                        </div>
                <div className="w-100 border-top mt-3"></div>
                <div className="action-uploader  align-self-start ">
                <FileUpload 
                    {...fileProps}
                    placeholder="DELIBERA DI ADOZIONE"
                    risorsa={deliberaAdozione} variables={{codice: uuid, tipo: "delibera_adozione" }}/>                
                </div>
                <div className="row mt-4">
                    <div className="col-12 d-flex pl-4 align-items-center">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA ADOZIONE" selected={dataDeliberaAdozione ? new Date(dataDeliberaAdozione) : undefined} getInput={getInput(uuid,"dataDeliberaAdozione")} className="py-0" mutation={UPDATE_ADOZIONE}/></div>
                </div>
                
                <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <Elaborati 
                        tipoPiano={tipoPiano.toLowerCase()} 
                        resources={edges}
                        mutation={ADOZIONE_FILE_UPLOAD}
                        resourceMutation={DELETE_RISORSA_ADOZIONE}
                        uuid={uuid}
                        />               
                <div className="w-100 border-top mt-3"></div>                
                <h5 className="pt-4 font-weight-light">PUBBLICAZIONE</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL B.U.R.T</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL B.U.R.T." getInput={getInput(uuid, "pubblicazioneBurtUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneBurtUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneBurtData ? new Date(pubblicazioneBurtData) : undefined} getInput={getInput(uuid, "pubblicazioneBurtData")} className="py-0 " mutation={UPDATE_ADOZIONE}/>
                    </div>

                </div>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL SITO</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL SITO" getInput={getInput(uuid, "pubblicazioneSitoUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneSitoUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneSitoData ? new Date(pubblicazioneSitoData) : undefined} getInput={getInput(uuid, "pubblicazioneSitoData")} className="py-0 " mutation={UPDATE_ADOZIONE}/>
                    </div>

                </div>
                <div className="w-100 border-top mt-3"></div>    
                <div className="row align-items-center pt-4 ">
                    <div className="col-12"><h5 className="mb-0 font-weight-light">INVIO A SCA E AC</h5>
                    </div>
                    {/* <div className="col-1">
                    <input  checked={true} className="form-check-input position-static" type="checkbox"/>
                    </div> */}
                
                
                <div className="col-12 pt-2">
                    {`Il sistema invierà i link ai Soggetti Compententi in materina ambientale e all'Autorità compentente
                    in materia ambientale (già selezionati nella fase di avvio) la documentazione necessaria affinché i destinatari
                    possano formulare i pareri entro 60gg dall'adozione`}
                </div>
                </div>
                <div className="w-100 border-top mt-3"></div> 

                <div className="row d-flex align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-dark text-serapide">ALERT RICEZIONI OSSERVAZIONI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-dark pr-1">date_range</i><span>{dataRicezioneOsservazioni && formatDate(dataRicezioneOsservazioni)}</span></div>
                    <div className="col-11 offset-1">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-serapide">ALERT RICEZIONI PARERI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-serapide pr-1">date_range</i><span>{dataRicezionePareri && formatDate(dataRicezionePareri)}</span></div>
                    <div className="col-11 offset-1">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di adozione</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-5">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_ADOZIONE} 
                        canCommit={ elaboratiCompleti && deliberaAdozione && dataDeliberaAdozione && pubblicazioneBurtUrl && pubblicazioneBurtData && pubblicazioneSitoUrl && pubblicazioneSitoData}></SalvaInvia>
                </div>
            </React.Fragment>)})

export default (props) => {
    const codice = getCodice(props)
    return (
        <Query query={GET_VAS} variables={{codice}} onError={showError}>
            {({loadingVas, data: {modello: {edges: [vas] = []} = {}} = {}}) => (
                <Query query={GET_ADOZIONE} variables={{codice}} onError={showError}>
                    {({loading, data: {modello: {edges: [proceduraAdozione] = []} = []} = {}}) => {
                        if (loading || loadingVas) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI {...props} vas={vas} proceduraAdozione={proceduraAdozione} />)}
                    }
                </Query>)}
        </Query>)}