/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import UploadFiles from '../../components/UploadFiles'
import  {showError, formatDate} from '../../utils'

import {Query, Mutation} from "react-apollo"
import Resource from '../../components/Resource'
import {EnhancedListSelector} from '../../components/ListSelector'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import AddContact from '../../components/AddContact'
import Button from '../../components/IconButton'
import TextWithTooltip from '../../components/TextWithTooltip'
import {EnhancedDateSelector} from '../../components/DateSelector'
import {rebuildTooltip} from '../../enhancers/utils'
import Input from '../../components/EnhancedInput'

import {GET_ADOZIONE, UPDATE_ADOZIONE, GET_VAS,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD,
    TRASMISSIONE_ADOZIONE
} from '../../graphql'


const getInput = (uuid, field) => (val) => (
    {variables:
        { input:{ 
            proceduraAdozione: { [field]: val}, 
            uuid
        }
}})


const getDateInput = (uuid,field) => (val) => ({
    variables: {
        input: { 
            proceduraAdozione: {
                [field]: val.toISOString()},
            uuid
        }
    }})

const getSuccess = ({uploadRisorsaAdozione: {success}} = {}) => success

// const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
//     return edges.map(({node: {nome, uuid, tipologia}}) => ({label: nome, value: uuid, tipologia}))
// }
const fileProps = {className: `border-0`, getSuccess, mutation: ADOZIONE_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_ADOZIONE, disabled: false, isLocked: false}
const UI = rebuildTooltip({onUpdate: true, log: true, comp: "AvvioProc"})(({
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
            redazioneNormeTecnicheAttuazioneUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl,
            autoritaIstituzionali: {edges: aut =[]} = {},
            altriDestinatari: {edges: dest = []} = {}
            },
        back}) => {

            
            const {node: rapportoAmbientale} = resVas.filter(({node: {tipo}}) => tipo === "rapporto_ambientale").shift() || {}
            const {node: deliberaAdozione} = edges.filter(({node: {tipo}}) => tipo === "delibera_adozione").shift() || {}
            const elaboratiAdozione = edges.filter(({node: {tipo}}) => tipo === "elaborati_adozione").map(({node}) => node)
            // const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            // const dests = dest.map(({node: {uuid} = {}} = {}) => uuid)
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Adozione
                </ActionTitle>
                <h5 className="pt-5 font-weight-light">RIFERIMENTI DOCUMENTALI</h5>
                <h6 className="pt-3 font-weight-light">NORME TECHINICHE DI ATTUAZIONE E RAPPORTO AMBIENTALE</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={redazioneNormeTecnicheAttuazioneUrl} target="_blank" className="pl-1 text-secondary">{redazioneNormeTecnicheAttuazioneUrl}</a>
                    </div>
                </div>
                <Resource useLabel fileSize={false} className="border-0 mt-3" icon="attach_file" resource={rapportoAmbientale}/>
                <h6 className="pt-3 font-weight-light">CONFORMAZIONE AL PIT-PPR</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={conformazionePitPprUrl} target="_blank" className="pl-1 text-secondary">{conformazionePitPprUrl}</a>
                    </div>
                </div>
                <h6 className="pt-3 font-weight-light">MONITORAGGIO URBANISTICO</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={monitoraggioUrbanisticoUrl} target="_blank" className="pl-1 text-secondary">{monitoraggioUrbanisticoUrl}</a>
                    </div>
                </div>
                <div className="w-100 border-top mt-3"></div>
                <h5 className="pt-4 font-weight-light">DESTINATARI</h5>
                <h6 className="font-weight-light pb-1 mt-2">SCELTA SOGGETTI ISTITUZIONALI</h6>
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
                    <EnhancedDateSelector placeholder="SELEZIONA DATA ADOZIONE" selected={dataDeliberaAdozione ? new Date(dataDeliberaAdozione) : undefined} getInput={getDateInput(uuid,"dataDeliberaAdozione")} className="py-0" mutation={UPDATE_ADOZIONE}/></div>
                </div>
                
                <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <UploadFiles 
                    {...fileProps}
                    risorse={elaboratiAdozione} 
                    variables={{codice: uuid, tipo: "elaborati_adozione" }}
                    getFileName={({uploadRisorsaAdozione: {fileName} = {}}) => fileName}/>
                
                <div className="w-100 border-top mt-3"></div>                
                <h5 className="pt-4 font-weight-light">PUBBLICAZIONE</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL B.U.R.T</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL B.U.R.T." getInput={getInput(uuid, "pubblicazioneBurtUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneBurtUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneBurtData ? new Date(pubblicazioneBurtData) : undefined} getInput={getDateInput(uuid, "pubblicazioneBurtData")} className="py-0 " mutation={UPDATE_ADOZIONE}/>
                    </div>

                </div>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL SITO</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL SITO" getInput={getInput(uuid, "pubblicazioneSitoUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneSitoUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneSitoData ? new Date(pubblicazioneSitoData) : undefined} getInput={getDateInput(uuid, "pubblicazioneSitoData")} className="py-0 " mutation={UPDATE_ADOZIONE}/>
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
                        canCommit={ deliberaAdozione && dataDeliberaAdozione && pubblicazioneBurtUrl && pubblicazioneBurtData && pubblicazioneSitoUrl && pubblicazioneSitoData}></SalvaInvia>
                </div>
            </React.Fragment>)})

export default ({back, piano}) => (
        <Query query={GET_VAS} variables={{codice: piano.codice}} onError={showError}>
            {({loadingVas, data: {procedureVas: {edges: vasEdges = []} = []} = {}}) => (
                <Query query={GET_ADOZIONE} variables={{codice: piano.codice}} onError={showError}>
                    {({loading, data: {procedureAdozione: {edges = []} = []} = {}}) => {
                        if(loading || loadingVas) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI vas={vasEdges[0]} proceduraAdozione={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)}
        </Query>)