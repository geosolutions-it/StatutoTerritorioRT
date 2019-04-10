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

import {GET_AVVIO, UPDATE_AVVIO,
    DELETE_RISORSA_AVVIO,
    AVVIO_FILE_UPLOAD, UPDATE_PIANO,
    GET_CONTATTI,
    AVVIA_PIANO
} from '../../queries'


const getInput = (codice, field) => (val) => (
    {variables:{ input:{ 
    pianoOperativo: { [field]: val}, codice}
}})



const getGaranteInput = (uuid) => (val) => ({
    variables: {
        input: { 
            proceduraAvvio: {
                garanteNominativo: val}, 
            uuid
        }
    }})
const getGarantePecInput = (uuid) => (val) => ({
        variables: {
            input: { 
                proceduraAvvio: {
                    garantePec: val}, 
            uuid
        }
}})
const getScadenzaInput = (uuid) => (val) => ({
    variables: {
        input: { 
            proceduraAvvio: {
                dataScadenzaRisposta: val.toISOString()},
            uuid
        }
    }})

const getSuccess = ({uploadRisorsaAvvio: {success}} = {}) => success

const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid, tipologia}}) => ({label: nome, value: uuid, tipologia}))
}
const fileProps = {className: `border-0`, getSuccess, mutation: AVVIO_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_AVVIO, disabled: false, isLocked: false}
const UI = rebuildTooltip({onUpdate: true, log: true, comp: "AvvioProc"})(({
    procedureAvvio: {node: {
            uuid, conferenzaCopianificazione, 
            garanteNominativo, garantePec,
            risorse: {edges=[]} = {}
            } = {}} = {}, 
        piano: {
            redazioneNormeTecnicheAttuazioneUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl,
            autoritaIstituzionali: {edges: aut =[]} = {},
            altriDestinatari: {edges: dest = []} = {},
            codice,    
            risorse: {edges: resPiano = []}} = {}, 
        back}) => {

            const {node: delibera} = resPiano.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            
            const deliberaAdozione = edges.filter(({node: {tipo}}) => tipo === "delibera_adozione").map(({node}) => node).shift()
            const elaboratiAdozione = edges.filter(({node: {tipo}}) => tipo === "elaborati_adozione").map(({node}) => node)
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const dests = dest.map(({node: {uuid} = {}} = {}) => uuid)
            const dataDelibera = undefined
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Adozione
                </ActionTitle>
                <h5 className="pt-5 font-weight-light">RIFERIMENTI DOCUMENTALI</h5>
                <h6 className="pt-3 font-weight-light">NORME TECHINICHE DI ATTUAZIONE E RAPPORTO AMBIENTALE</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><div className="pl-1">{redazioneNormeTecnicheAttuazioneUrl}</div>
                    </div>
                </div>
                <Resource useLabel fileSize={false} className="border-0 mt-3" icon="attach_file" resource={delibera}/>
                <h6 className="pt-3 font-weight-light">CONFORMAZIONE AL PIT-PPR</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><div className="pl-1">{conformazionePitPprUrl}</div>
                    </div>
                </div>
                <h6 className="pt-3 font-weight-light">MONITORAGGIO URBANISTICO</h6>
                <div className="mt-1 row d-flex align-items-center">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><div className="pl-1">{conformazionePitPprUrl}</div>
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
                    <EnhancedDateSelector placeholder="SELEZIONA DATA ADOZIONE" selected={dataDelibera ? new Date(dataDelibera) : undefined} getInput={getScadenzaInput(uuid)} className="py-0" mutation={UPDATE_AVVIO}/></div>
                </div>
                
                <h6 className="font-weight-light pt-5 pl-2 pb-1">ELABORATI DEL PIANO</h6>
                <UploadFiles 
                    {...fileProps}
                    risorse={elaboratiAdozione} 
                    variables={{codice: uuid, tipo: "elaborati_adozione" }}
                    getFileName={({uploadRisorsaAvvio: {fileName} = {}}) => fileName}/>
                
                <div className="w-100 border-top mt-3"></div>                
                <h5 className="pt-4 font-weight-light">PUBBLICAZIONE</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL B.U.R.T</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL B.U.R.T." getInput={getInput(codice, "redazioneNormeTecnicheAttuazioneUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={undefined} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={dataDelibera ? new Date(dataDelibera) : undefined} getInput={getScadenzaInput(uuid)} className="py-0 " mutation={UPDATE_AVVIO}/>
                    </div>

                </div>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3">URL SITO</div>
                    <div className="col-9 ">
                        <Input placeholder="COPIA URL SITO" getInput={getInput(codice, "redazioneNormeTecnicheAttuazioneUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={undefined} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={dataDelibera ? new Date(dataDelibera) : undefined} getInput={getScadenzaInput(uuid)} className="py-0 " mutation={UPDATE_AVVIO}/>
                    </div>

                </div>
                <div className="w-100 border-top mt-3"></div>    
                <div className="row align-items-center pt-4 ">
                    <div className="col-11"><h5 className="mb-0 font-weight-light">INVIO A SCA E AC</h5>
                    </div>
                    <div className="col-1">
                    <input  checked={true} className="form-check-input position-static" type="checkbox"/>
                    </div>
                
                
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
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-dark pr-1">date_range</i><span>22/12/2019</span></div>
                    <div className="col-11 offset-1">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-serapide">ALERT RICEZIONI PARERI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-serapide pr-1">date_range</i><span>22/12/2019</span></div>
                    <div className="col-11 offset-1">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di adozione</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-5">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={AVVIA_PIANO} canCommit={ auths.length > 0  &&  garanteNominativo && garantePec}></SalvaInvia>
                
                </div>
            </React.Fragment>)})

export default ({back, piano}) => (
                <Query query={GET_AVVIO} variables={{codice: piano.codice}} onError={showError}>
                    {({loading, data: {procedureAvvio: {edges = []} = []} = {}}) => {
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI procedureAvvio={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)