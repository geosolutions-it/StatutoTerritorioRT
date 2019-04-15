/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {EnhancedSwitch} from './Switch'
import FileUpload from './UploadSingleFile'
import Button from './IconButton'
import {formatDate, getNominativo, showError} from '../utils'
import {EnhancedListSelector} from './ListSelector'
import Resource from '../components/Resource'
import {GET_CONTATTI, GET_VAS, VAS_FILE_UPLOAD, DELETE_RISORSA_VAS, UPDATE_VAS, UPDATE_PIANO, PROMUOVI_PIANO, GET_CONSULTAZIONE_VAS} from '../graphql'
import { Query, Mutation} from 'react-apollo';
import { toast } from 'react-toastify'
import AddContact from '../components/AddContact'
import SalvaInvia from '../components/SalvaInvia'
import TextWithTooltip from '../components/TextWithTooltip'
import  {rebuildTooltip} from '../enhancers/utils'
import {map}  from 'lodash'



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

const checkAnagrafica =  (tipologia = "" , sP, auths, scas, semplificata, verifica, docProcSemp) => {
    switch (tipologia.toLowerCase()) {
        case "semplificata":
        return semplificata && auths.length > 0 && !!sP
        case "verifica":
        return verifica && auths.length > 0 && scas.length > 0 && !!sP
        case "procedimento":
        return auths.length > 0 && scas.length > 0 && !!sP
        case "non_necessaria":
        return !!sP
        case "procedimento_semplificato":
        return docProcSemp && auths.length > 0 && scas.length > 0 && !!sP
        default:
        return false
    }
}
const fileProps = {className:"col-xl-12",
                    mutation: VAS_FILE_UPLOAD, resourceMutation: DELETE_RISORSA_VAS}


const UI = rebuildTooltip({onUpdate: false})(({codice, consultazioneSCA = {}, canUpdate, isLocked, Vas = {}}) => {
            
    const {node: {uuid, tipologia, dataAssoggettamento, assoggettamento,
        piano: {soggettoProponente: sP, autoritaCompetenteVas: {edges: aut =[]} = {}, soggettiSca: {edges: sca = []} = {}} = {}, risorse : {edges: resources = []} = {}} = {}} = Vas
    const {node: {avvioConsultazioniSca, dataAvvioConsultazioniSca, dataRicezionePareri, dataScadenza} = {}} = consultazioneSCA
    const {node: semplificata}= resources.filter(({node: n}) => n.tipo === "vas_semplificata").pop() || {};
    const {node: verifica} = resources.filter(({node: n}) => n.tipo === "vas_verifica").pop() || {};
    const {node: docProcSemp} = resources.filter(({node: n}) => n.tipo === "doc_proc_semplificato").pop() || {};
    
    const disableSCA = tipologia === "SEMPLIFICATA" || tipologia === "NON_NECESSARIA"
    const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
    const scas = sca.map(({node: {uuid} = {}} = {}) => uuid)
    const canCommit = !isLocked && canUpdate && checkAnagrafica(tipologia, sP, auths, scas, semplificata, verifica, docProcSemp)

    const pareriUser =  resources.filter(({node: {tipo}}) => tipo === "parere_sca").reduce((acc, {node}) => {
        if (acc[node.user.fiscalCode]) { 
            acc[node.user.fiscalCode].push(node)
        }
        else {
            acc[node.user.fiscalCode] = [node]
        }
        return acc
    } , {})


    return(
    <React.Fragment>
        <span className="pt-4">PROCEDIMENTO VAS</span>
        {!isLocked && (<span className="p-3 pb-5">NOTA : Le opzioni sono escludenti. Se viene selezionata la richiesta della VAS semplificata
            è richiesto l’upload della Relazione Motivata; se viene selezionata la Richiesta di Verifica VAS è richiesto
    l’upload del documento preliminare di verifica; se si seleziona il Procedimento Vas si decide di seguire il procedimento VAS esteso.</span>)}
        <EnhancedSwitch isLocked={isLocked} 
                        getInput={getVasTypeInput(uuid)} 
                        mutation={UPDATE_VAS} 
                        value="semplificata" checked={tipologia === "SEMPLIFICATA"}  
                        label={(<TextWithTooltip dataTip="art.5 co.3ter L.R. 10/2010" text="PROCEDIMENTO DI VERIFICA SEMPLIFICATA"/>)}
                        className="mt-5 mb-4">
            {(checked) =>
                <div className="row">
                <FileUpload  {...fileProps}
                                disabled={!checked} 
                                isLocked={!checked || isLocked}
                                risorsa={semplificata} 
                                placeholder={(<TextWithTooltip dataTip="art.5 co.3ter L.R. 10/2010" text="Relazione motivata per VAS semplificata"/>)}
                                variables={{codice: uuid, tipo: "vas_semplificata" }}/>
                </div>
            }
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked}
            getInput={getVasTypeInput(uuid)} 
            mutation={UPDATE_VAS} 
            value="verifica" 
            checked={tipologia === "VERIFICA"}  
            label={(<TextWithTooltip dataTip="art.22 L.R. 10/2010" text="RICHIESTA VERIFICA DI  ASSOGGETTABILITA'"/>)}
            className="mt-5 mb-4">
            {(checked) => <div className="row">
                <FileUpload {...fileProps}
                            disabled={!checked} isLocked={!checked || isLocked}
                            risorsa={verifica}
                            placeholder={(<TextWithTooltip dataTip="art.22 L.R. 10/2010" text="Documento preliminare"/>)}
                            variables={{codice: uuid, tipo: "vas_verifica" }}/>
                    </div>}
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked} 
            getInput={getVasTypeInput(uuid)}
            mutation={UPDATE_VAS}
            value="procedimento_semplificato"
            label={(<TextWithTooltip dataTip="art.8 co.5 L.R. 10/2010" text="PROCEDIMENTO SEMPLIFICATO"/>)}
            checked={tipologia === "PROCEDIMENTO_SEMPLIFICATO"}
            className="mt-5 mb-4">
            {(checked) => <div className="row">
                <FileUpload {...fileProps}
                            disabled={!checked} isLocked={!checked || isLocked}
                            risorsa={docProcSemp}
                            placeholder={(<TextWithTooltip dataTip="art. 8, 22 e 23 L.R. 10/2010" text="Documento preliminare"/>)}
                            variables={{codice: uuid, tipo: "doc_proc_semplificato" }}/>
                    </div>}
            </EnhancedSwitch>
        <EnhancedSwitch isLocked={isLocked} 
            getInput={getVasTypeInput(uuid)}
            mutation={UPDATE_VAS}
            value="procedimento"
            checked={tipologia === "PROCEDIMENTO"}
            label="PROCEDIMENTO VAS (AVVIO)"
            className="mt-5">
            {() => (
                <div className="row">
                <span className="p-3 col-xl-12">Scegliendo “Procedura VAS” verrà inviata una comunicazione all’autorità procedente e proponente (AP/P)
            che avvierà le consultazioni degli Soggetti Competenti in Materia Ambientale (SCA)</span></div>
                
            )}
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked}
            getInput={getVasTypeInput(uuid)}
            mutation={UPDATE_VAS}
            value="non_necessaria"
            checked={tipologia === "NON_NECESSARIA"}
            label="VAS NON NECESSARIA"
            className="mt-5">
                {() =>(<div className="row"><span className="p-3 mb-5 col-xl-12">In questo caso per il piano non è necessaria alcuna VAS </span></div>)}
        </EnhancedSwitch>
        <div className="d-flex mt-2 pt-2 justify-content-between mb-3">
            <div style={{minWidth: "33%"}}>
                { !isLocked ? (<Mutation mutation={UPDATE_PIANO} onError={showError}>
                {(onChange) => {
                        const changed = (val) => {
                            let soggettoProponenteUuid = val;
                            if(sP && sP.uuid === val){
                                soggettoProponenteUuid = ""
                            }
                            onChange({variables:{ input:{ 
                                        pianoOperativo: { soggettoProponenteUuid}, codice}
                                }})
                        }
                        return (
                    <EnhancedListSelector
                            selected={sP ? [sP.uuid] : []}
                            query={GET_CONTATTI}
                            variables={{tipo: "generico"}}
                            getList={getAuthorities}
                            label="DEFINISCI SOGGETTO PROPONENTE"
                            size="lg"
                            onChange={changed}
                            btn={(toggleOpen) => (<Button fontSize="60%" disabled={isLocked} onClick={toggleOpen} className="my-auto text-uppercase" color="serapide" icon="add_circle" label="SOGGETTO PROPONENTE"></Button>)}
                        >
                        <AddContact className="mt-2" tipologia="generico"></AddContact>
                        </EnhancedListSelector>)}
                    }
                </Mutation>) : (<span>SOGGETTO PROPONENTE</span>) }
                    {sP && sP.nome && (<div className="d-flex pt-3" key={sP.uuid}>
                            <i className="material-icons text-serapide">bookmark</i>
                            {sP.nome}
                    </div>)}
                </div>
            <div style={{minWidth: "33%"}}>
            { !isLocked ? (<Mutation mutation={UPDATE_PIANO} onError={showError}>
                {(onChange) => {
                    const changed = (val) => {
                        const autoritaCompetenteVas = auths.indexOf(val) !== -1 ? [] : [val]
                        onChange({variables:{ input:{ 
                                    pianoOperativo: { autoritaCompetenteVas}, codice}
                            }})
                    }
                    return (
                        <EnhancedListSelector
                            selected={auths}
                            query={GET_CONTATTI}
                            getList={getAuthorities}
                            onChange={changed}
                            variables={{tipo: "acvas"}}
                            size="lg"
                            label="SELEZIONA AUTORITA’ COMPETENTE VAS"
                            btn={(toggleOpen) => (<Button  fontSize="60%" disabled={isLocked} onClick={toggleOpen} className="text-uppercase" color="serapide" icon="add_circle" label="AUTORITA’ COMPETENTE VAS (AC)"/>)}
                            >
                            <AddContact className="mt-2" tipologia="acvas"></AddContact>
                            </EnhancedListSelector>)}
                }
                </Mutation>) : (<span>AUTORITA’ COMPETENTE VAS</span>) }
                {aut.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pt-3" key={uuid}>
                            <i className="material-icons text-serapide">bookmark</i>
                            {nome}
                </div>))}
            </div>
            <div style={{minWidth: "33%"}}>
            { !isLocked ? ( <Mutation mutation={UPDATE_PIANO} onError={showError}>
            {(onChange) => {
                    const changed = (val) => {
                        let nscas = []
                        if(scas.indexOf(val)!== -1){
                            nscas = scas.filter( uuid => uuid !== val)
                        }else {
                            nscas = scas.concat(val)
                        }
                        onChange({variables:{ input:{ 
                                    pianoOperativo: { soggettiSca: nscas}, codice}
                            }})
                    }
                    return (
                <EnhancedListSelector
                        selected={scas}
                        query={GET_CONTATTI}
                        variables={{tipo: "sca"}}
                        getList={getAuthorities}
                        label="DEFINISCI SCA"
                        size="lg"
                        onChange={changed}
                        btn={(toggleOpen) => (<Button fontSize="60%" onClick={toggleOpen} className="my-auto text-uppercase" disabled={disableSCA || isLocked} color="serapide" icon="add_circle" label="SOGGETTI COMPETENTI IN MATERIA AMBIENTALE (SCA)"></Button>)}
                    >
                    <AddContact className="mt-2" tipologia="sca"></AddContact>
                    </EnhancedListSelector>)}
                }
                </Mutation>) : (<span>SOGGETTI COMPETENTI IN MATERIA AMBIENALE</span>) }
                {sca.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pt-3" key={uuid}>
                            <i className="material-icons text-serapide">bookmark</i>
                            {nome}
                </div>))}
            </div>
        </div>
        {!isLocked && (<div className="d-flex mt-5 pt-5  justify-content-end">
                <SalvaInvia mutation={PROMUOVI_PIANO} variables={{codice}} canCommit={canCommit}></SalvaInvia>
        </div>)}
            {/* Mosrta il resto delle aprocedura vas quando simo in riassunot  i casi sono molteplici, 
                ho richiesta di verifica, ho richiesta verifica semplificata, richiesta procedimento richiesta procedimento semplificato, se la vas non è necessaia non aggiungo nulla
            */}
        { isLocked && (tipologia === "VERIFICA"  || tipologia === "SEMPLIFICATA") && (
            <div className="row pt-5">
                <div className="col-5 d-flex">
                        <i className="material-icons text-serapide self-align-center">{assoggettamento && "check_box" || "check_box_outline_blank"}</i>
                        <span className="pl-1">ESITO: {assoggettamento && "Assoggettamento VAS" || "Esclusione VAS"}</span>
                </div>
                <span className="col-4">{dataAssoggettamento && formatDate(dataAssoggettamento)}</span>            
            </div>)
        }
        { avvioConsultazioniSca && (
            <div className="row pt-5">
            <div className="col-5 d-flex">
                    <i className="material-icons text-serapide self-align-center">check_box</i>
                        <span className="pl-1">Avvio Consultazioni SCA</span>
                </div>
                <span className="col-4">{dataAvvioConsultazioniSca && formatDate(dataAvvioConsultazioniSca)}</span> 
            <div className="col-12 pt-2"></div>
            {map(pareriUser, (u) => (
                <div key={u[0].user.fiscalCode} className="col-12 pt-4">
                    <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                    {u.map(parere => (<Resource key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Resource>))}
                </div>
                ))
                }
            </div>

        )}
    </React.Fragment>)})



export default ({codice, canUpdate, isLocked}) => {
    return (
        <Query query={GET_VAS} variables={{codice}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []} = {}}) => (
                <Query query={GET_CONSULTAZIONE_VAS} variables={{codice}} onError={showError}>
                {({loadingC, data: {consultazioneVas: {edges: cons = []} = []} = {}}) => {
                if(loading || loadingC){
                    return (
                    <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    </div>)
                }
            return <UI codice={codice}  consultazioneSCA={cons[0]} canUpdate={canUpdate} isLocked={isLocked} Vas={edges[0]}/>
            }}
            </Query>)}
        </Query>)
    } 