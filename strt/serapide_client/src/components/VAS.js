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

import {EnhancedListSelector} from './ListSelector'
import {GET_CONTATTI, GET_VAS, VAS_FILE_UPLOAD, DELETE_RISORSA_VAS, UPDATE_VAS, UPDATE_PIANO, PROMUOVI_PIANO} from '../queries'
import { Query, Mutation} from 'react-apollo';
import { toast } from 'react-toastify'
import AddContact from '../components/AddContact'
import Confirm from '../components/ConfirmToast'

const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success
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

const showError = (error) => {
    toast.error(error.message,  {autoClose: true})
}
const checkAnagrafica =  (tipologia = "" , sP, auths, scas, semplificata, verifica) => {
    switch (tipologia.toLowerCase()) {
        case "semplificata":
        return semplificata && auths.length > 0 && !!sP
        case "verifica":
        return verifica && auths.length > 0 && scas.length > 0 && !!sP
        case "procedimento":
        return auths.length > 0 && scas.length > 0 && !!sP
        case "non_necessaria":
        return !!sP
        default:
        return false
    }
}

export default ({codice, canUpdate, isLocked}) => {
    return (
        <Query query={GET_VAS} variables={{codice}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []} = {}}) => {
                if(loading){
                    return (
                    <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    </div>)
            }
            
            const {node: {uuid, tipologia, piano: {soggettoProponente: sP, autoritaCompetenteVas: {edges: aut =[]} = {}, soggettiSca: {edges: sca = []} = {}} = {}, risorse : {edges: resources = []} = {}} = {}} = edges[0] || {}
            const {node: semplificata}= resources.filter(({node: n}) => n.tipo === "vas_semplificata").pop() || {};
            const {node: verifica} = resources.filter(({node: n}) => n.tipo === "vas_verifica").pop() || {};
            const disableSCA = tipologia === "SEMPLIFICATA" || tipologia === "NON_NECESSARIA"
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const scas = sca.map(({node: {uuid} = {}} = {}) => uuid)
            const canCommit = !isLocked && canUpdate && checkAnagrafica(tipologia, sP, auths, scas, semplificata, verifica)



            return(
            <React.Fragment>
                <span className="pt-4">PROCEDIMENTO VAS</span>
                {!isLocked && (<span className="pt-2">NOTA : Le opzioni sono escludenti. Se viene selezionata la richiesta della VAS semplificata
                    è richiesto l’upload della Relazione Motivata; se viene selezionata la Richiesta di Verifica VAS è richiesto
            l’upload del documento preliminare di verifica; se si seleziona il Procedimento Vas si decide di seguire il procedimento VAS esteso.</span>)}
                <EnhancedSwitch isLocked={isLocked} getInput={getVasTypeInput(uuid)} mutation={UPDATE_VAS} value="semplificata" checked={tipologia === "SEMPLIFICATA"}  label="RICHIESTA VAS SEMPLIFICATA" className="mt-3 vas-EnhancedSwitch justify-content-between">
                    {(checked) =>
                        <FileUpload getSuccess={getSuccess}  mutation={VAS_FILE_UPLOAD} resourceMutation={DELETE_RISORSA_VAS} disabled={!checked} isLocked={!checked || isLocked} risorsa={semplificata} placeholder="Relazione motivata per VAS semplificata" variables={{codice: uuid, tipo: "vas_semplificata" }}/>
                    }
                </EnhancedSwitch>
                <EnhancedSwitch  isLocked={isLocked} getInput={getVasTypeInput(uuid)}  mutation={UPDATE_VAS} value="verifica" checked={tipologia === "VERIFICA"}  label="RICHIESTA VERIFICA VAS" className=" justify-content-between vas-EnhancedSwitch mb-2">
                    {(checked) => <FileUpload getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} resourceMutation={DELETE_RISORSA_VAS} disabled={!checked} isLocked={!checked || isLocked} risorsa={verifica} placeholder="Documento preliminare di verifica" variables={{codice: uuid, tipo: "vas_verifica" }}/>}
                </EnhancedSwitch>
                <EnhancedSwitch isLocked={isLocked} getInput={getVasTypeInput(uuid)}  mutation={UPDATE_VAS} value="procedimento" checked={tipologia === "PROCEDIMENTO"}  label="PROCEDIMENTO VAS (AVVIO)" className=" justify-content-between vas-EnhancedSwitch mb-2">
                    {() => (
                        <span className="p-3">Scegliendo “Procedura VAS” verrà inviata una comunicazione all’autorità procedente e proponente (AP/P)
                    che avvierà le consultazioni degli Soggetti Competenti in Materia Ambientale (SCA)</span>
                        
                    )}
                </EnhancedSwitch>
                <EnhancedSwitch  isLocked={isLocked} getInput={getVasTypeInput(uuid)} mutation={UPDATE_VAS} value="non_necessaria"  checked={tipologia === "NON_NECESSARIA"}  label="VAS NON NECESSARIA" className=" justify-content-between vas-EnhancedSwitch">
                        {() =>(<span className="p-3">In questo caso per il piano non è necessaria alcuna VAS </span>)}
                </EnhancedSwitch>
                <div className="d-flex mt-4 justify-content-between mb-3">
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
                                    btn={(toggleOpen) => (<Button disabled={isLocked} onClick={toggleOpen} className="my-auto text-uppercase" color="warning" icon="add_circle" label="SOGGETTO PROPONENTE"></Button>)}
                                >
                                <AddContact className="mt-2" tipologia="generico"></AddContact>
                                </EnhancedListSelector>)}
                            }
                        </Mutation>) : (<span>SOGGETTO PROPONENTE</span>) }
                            {sP && sP.nome && (<div className="d-flex pt-3" key={sP.uuid}>
                                    <i className="material-icons text-warning">bookmark</i>
                                    {sP.nome}
                            </div>)}
                        </div>
                    <div style={{minWidth: "33%"}}>
                    { !isLocked ? (<Mutation mutation={UPDATE_PIANO} onError={showError}>
                        {(onChange) => {
                            const changed = (val) => {
                                onChange({variables:{ input:{ 
                                            pianoOperativo: { autoritaCompetenteVas: [val]}, codice}
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
                                    btn={(toggleOpen) => (<Button  disabled={isLocked} onClick={toggleOpen} className="text-uppercase" color="warning" icon="add_circle" label="IDENTIFICA L’AUTORITA’ COMPETENTE VAS (AC)"/>)}
                                    >
                                    <AddContact className="mt-2" tipologia="acvas"></AddContact>
                                    </EnhancedListSelector>)}
                        }
                        </Mutation>) : (<span>AUTORITA’ COMPETENTE VAS</span>) }
                        {aut.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pt-3" key={uuid}>
                                 <i className="material-icons text-warning">bookmark</i>
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
                                btn={(toggleOpen) => (<Button onClick={toggleOpen} className="my-auto text-uppercase" disabled={disableSCA || isLocked} color="warning" icon="add_circle" label="IDENTIFICA SOGGETTI COMPETENTI IN MATERIA AMBIENTALE (SCA)"></Button>)}
                            >
                            <AddContact className="mt-2" tipologia="sca"></AddContact>
                            </EnhancedListSelector>)}
                        }
                        </Mutation>) : (<span>SOGGETTI COMPETENTI IN MATERIA AMBIENALE</span>) }
                        {sca.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pt-3" key={uuid}>
                                 <i className="material-icons text-warning">bookmark</i>
                                 {nome}
                        </div>))}
                    </div>
                </div>
                {!isLocked && (<div className="d-flex  justify-content-center">
                    <Mutation mutation={PROMUOVI_PIANO} onError={showError}>
                    {(onConfirm, {loading}) => {
                        let toastId
                        const updatePiano = (code) => {onConfirm({variables: {codice: code}})}
                        const confirm = () => {
                            if(!toast.isActive(toastId)) {
                            toastId = toast.warn(<Confirm confirm={updatePiano} id={codice} label="Confermi invio Anagrafica?" />, {
                                autoClose: true,
                                draggable: true,
                                onClose: ( ) => {toastId = null}
                              });
                            }
                        }
                      return (<Button isLoading={loading} onClick={confirm} className="my-auto text-uppercase" disabled={!canCommit} color="warning"  label="SALVA ED INVIA"></Button>)
                    }}
                    </Mutation>
                </div>)}
            </React.Fragment>)}}
         </Query>)
        }