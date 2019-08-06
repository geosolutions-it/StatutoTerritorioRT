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
import ListaContatti from 'components/ListaContatti'
import Spinner from 'components/Spinner'

import {EnhancedDateSelector} from 'components/DateSelector'
import Input from 'components/EnhancedInput'
import Elaborati from "components/ElaboratiPiano"


import  {showError, formatDate, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE, UPDATE_ADOZIONE, GET_VAS,
    DELETE_RISORSA_ADOZIONE,
    ADOZIONE_FILE_UPLOAD,
    TRASMISSIONE_ADOZIONE
} from 'schema'


const Link = ({title, url}) => (<React.Fragment>
                <ActionSubParagraphTitle>{title}</ActionSubParagraphTitle>
                <div className="mt-3 row d-flex align-items-center">
                    <div className="col-12 d-flex align-items-center">
                        <i className="material-icons icon-15 text-serapide">link</i><a href={url} target="_blank" rel="noopener noreferrer" className="pl-1 size-12 text-secondary">{url}</a>
                    </div>
                </div>
                    </React.Fragment>)
 

const getInput = getInputFactory("proceduraAdozione")

const fileProps = {className: `border-0`, mutation: ADOZIONE_FILE_UPLOAD,
                    resourceMutation: DELETE_RISORSA_ADOZIONE, disabled: false, isLocked: false,
                    iconSize: "icon-15", fontSize: "size-11",
                    vertical: true, useLabel: true}
                    
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
            // altriDestinatari: {edges: dest = []} = {}
            },
        back}) => {

            const {node: rapportoAmbientale} = resVas.filter(({node: {tipo}}) => tipo === "rapporto_ambientale").shift() || {}
            const {node: deliberaAdozione} = edges.filter(({node: {tipo}}) => tipo === "delibera_adozione").shift() || {}
            return (<React.Fragment>
                <ActionTitle>
                   Trasmissione Adozione
                </ActionTitle>
                <ActionParagraphTitle>RIFERIMENTI DOCUMENTALI</ActionParagraphTitle>
                <Link title="NORME TECNICHE DI ATTUAZIONE E RAPPORTO AMBIENTALE" url={redazioneNormeTecnicheAttuazioneUrl}/>
                <Resource iconSize="icon-15" fontSize="size-11" useLabel fileSize={false} className="border-0 mt-3" icon="attach_file" resource={rapportoAmbientale}/>
                <div className="w-100 py-2"></div>
                <Link title="CONFORMAZIONE AL PIT-PPR" url={conformazionePitPprUrl}/>
                <div className="w-100 py-2"></div>
                <Link title="MONITORAGGIO URBANISTICO" url={monitoraggioUrbanisticoUrl}/>
                <div className="w-100 border-top m-0 mt-4"></div>
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
                <ActionParagraphTitle>PUBBLICAZIONE</ActionParagraphTitle>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3 size-12">URL B.U.R.T</div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder="COPIA URL B.U.R.T." getInput={getInput(uuid, "pubblicazioneBurtUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneBurtUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector  placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneBurtData ? new Date(pubblicazioneBurtData) : undefined} getInput={getInput(uuid, "pubblicazioneBurtData")} className="py-0 ml-2 rounded-pill size-8 icon-13" mutation={UPDATE_ADOZIONE}/>
                    </div>

                </div>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-3 size-12">URL SITO</div>
                    <div className="col-9 ">
                        <Input className="size-10" placeholder="COPIA URL SITO" getInput={getInput(uuid, "pubblicazioneSitoUrl")} mutation={UPDATE_ADOZIONE} disabled={false}  onChange={undefined} value={pubblicazioneSitoUrl} type="text" />
                    </div>
                    <div className="col-9 mt-2 offset-3">
                    <EnhancedDateSelector placeholder="SELEZIONA DATA PUBBLICAZIONE" selected={pubblicazioneSitoData ? new Date(pubblicazioneSitoData) : undefined} getInput={getInput(uuid, "pubblicazioneSitoData")} className="py-0 ml-2 rounded-pill size-8 icon-13" mutation={UPDATE_ADOZIONE}/>
                    </div>

                </div>
                <div className="w-100 border-top mt-3"></div>    
                <ActionParagraphTitle className="mb-0 font-weight-light">INVIO A SCA E AC</ActionParagraphTitle>

                
                <div className="pt-3 text-justify size-13">
                    {`Il sistema invierà i link ai Soggetti Compententi in materia ambientale e all'Autorità compentente
                    in materia ambientale (già selezionati nella fase di avvio) la documentazione necessaria affinché i destinatari
                    possano formulare i pareri entro 60gg dall'adozione`}
                </div>
                <div className="w-100 border-top mt-3"></div> 

                <div className="row d-flex align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide icon-16">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-dark text-serapide size-13">ALERT RICEZIONI OSSERVAZIONI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-dark pr-1 icon-16">date_range</i><span>{dataRicezioneOsservazioni && formatDate(dataRicezioneOsservazioni)}</span></div>
                    <div className="col-11 offset-1 size-12">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di pubblicazione su B.U.R.T. e sul sito web</div>
                </div>
                <div className="row align-items-center pt-4">
                    <div className="col-1"><i className="material-icons text-serapide icon-18">notifications_active</i></div>
                    <div className="col-7"><div className="pl-1 py-1 bg-serapide size-13">ALERT RICEZIONI PARERI</div></div>
                    <div className="col-3 d-flex align-items-center p-0"><i className="material-icons text-serapide pr-1 icon-16">date_range</i><span>{dataRicezionePareri && formatDate(dataRicezionePareri)}</span></div>
                    <div className="col-11 offset-1 size-12">Il sistema calcola automaticamente la data entro la quale ricevere le osservazioni sulla base
                    della data di adozione</div>
                </div>
                
                <div className="w-100 border-top mt-3"></div> 
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_ADOZIONE} 
                        canCommit={ deliberaAdozione && dataDeliberaAdozione && pubblicazioneBurtUrl && pubblicazioneBurtData && pubblicazioneSitoUrl && pubblicazioneSitoData}></SalvaInvia>
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
                            return <Spinner/>
                        }
                        return (
                            <UI {...props} vas={vas} proceduraAdozione={proceduraAdozione} />)}
                    }
                </Query>)}
        </Query>)}