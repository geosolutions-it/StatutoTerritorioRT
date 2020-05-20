/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Query, Mutation} from 'react-apollo';

import {EnhancedSwitch} from './Switch'
import FileUpload from './UploadSingleFile'
import Button from './IconButton'
import {EnhancedListSelector} from './ListSelector'

// import AddContact from 'components/AddContact'
import SalvaInvia from 'components/SalvaInvia'
import TextWithTooltip from 'components/TextWithTooltip'

import  {rebuildTooltip} from 'enhancers'

import { showError, getInputFactory, getContatti, VAS_DOCS, VAS_TYPES} from 'utils'

import {GET_CONTATTI, GET_VAS, VAS_FILE_UPLOAD,
    DELETE_RISORSA_VAS, UPDATE_VAS, UPDATE_PIANO,
    PROMUOVI_PIANO} from 'schema'


const getVasTypeInput = getInputFactory("proceduraVas")


const checkDoc = (tipologia, resources) => {
    if(tipologia === VAS_TYPES.NON_NECESSARIA  && tipologia === VAS_TYPES.PROCEDURA_ORDINARIA) {
        return true;
    }
    const {node: doc} = resources.filter(({node: n}) => n.tipo === VAS_DOCS[tipologia]).pop() || {};
    return !!doc;
}


const checkSoggetti =  (tipologia = "" , sP, ac, scas) => {
    if(!!sP) {
        return false;
    }
    switch (tipologia) {
        case VAS_TYPES.VERIFICA_SEMPLIFICATA:
        case VAS_TYPES.VERIFICA:
        return ac.length > 0
        case VAS_TYPES.PROCEDURA_ORDINARIA:
        case VAS_TYPES.PROCEDIMENTO_SEMPLIFICATO:
        return ac.length > 0 && scas.length > 0
        default:
        return false
    }
}
// Proprietà comuni upload files
const fileProps = {className:"col-xl-12", iconSize: "icon-24", fontSize: "size-15",
                    mutation: VAS_FILE_UPLOAD, resourceMutation: DELETE_RISORSA_VAS}


const UI = rebuildTooltip({onUpdate: false})(({codice, canUpdate, isLocked, Vas = {}}) => {
    
    const {node: {uuid, tipologia, piano: { soggettoProponente, soggettiOperanti = [] } = {}, risorse : {edges: resources = []} = {}} = {}} = Vas
        
    const {ufficio: sP = {}} = soggettoProponente || {};

    
    const {node: semplificata}= resources.filter(({node: n}) => n.tipo === VAS_DOCS.REL_MOT).pop() || {};
    const {node: verifica} = resources.filter(({node: n}) => n.tipo === VAS_DOCS.DOC_PRE_VER_VAS).pop() || {};
    const {node: docProcSemp} = resources.filter(({node: n}) => n.tipo === VAS_DOCS.DOC_PRE_VAS).pop() || {};
    

    const disableSCA = tipologia === VAS_TYPES.NON_NECESSARIA
    const acs = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "AC").map(({qualificaUfficio} = {}) => (qualificaUfficio))
    const scas = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))
    const canCommit = !isLocked && canUpdate && checkSoggetti(tipologia, sP, acs, scas) && checkDoc(tipologia, resources)
    const getInputTipologia = getVasTypeInput(uuid, "tipologia")


    return(
    <React.Fragment>
        <span className="pt-4">PROCEDIMENTO VAS</span>
        <span className="p-3 pb-5">NOTA : Le opzioni sono escludenti. Se viene selezionata la richiesta della VAS semplificata
            è richiesto l’upload della Relazione Motivata; se viene selezionata la Richiesta di Verifica VAS è richiesto
    l’upload del documento preliminare di verifica; se si seleziona il Procedimento Vas si decide di seguire il procedimento VAS esteso.</span>
        <EnhancedSwitch isLocked={isLocked}
                        getInput={getInputTipologia}
                        mutation={UPDATE_VAS}
                        value={VAS_TYPES.VERIFICA_SEMPLIFICATA} checked={tipologia === VAS_TYPES.VERIFICA_SEMPLIFICATA}
                        label={(<TextWithTooltip dataTip="art.5 co.3ter L.R. 10/2010" text="PROCEDURA DI VERIFICA SEMPLIFICATA"/>)}
                        className="mt-5 mb-4">
            {(checked) =>
                <div className="row">
                <FileUpload  {...fileProps}
                                disabled={!checked}
                                isLocked={!checked || isLocked}
                                risorsa={semplificata}
                                placeholder={(<TextWithTooltip dataTip="art.5 co.3ter L.R. 10/2010" text="Relazione motivata per verifica VAS semplificata"/>)}
                                variables={{codice: uuid, tipo: VAS_DOCS.REL_MOT}}/>
                </div>
            }
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked}
            getInput={getInputTipologia}
            mutation={UPDATE_VAS}
            value={VAS_TYPES.VERIFICA}
            checked={tipologia === VAS_TYPES.VERIFICA}
            label={(<TextWithTooltip dataTip="art.22 L.R. 10/2010" text="PROCEDURA DI VERIFICA DI ASSOGGETTABILITA’ A VAS"/>)}
            className="mt-5 mb-4">
            {(checked) => <div className="row">
                <FileUpload {...fileProps}
                            disabled={!checked} isLocked={!checked || isLocked}
                            risorsa={verifica}
                            placeholder={(<TextWithTooltip dataTip="art.22 L.R. 10/2010" text="Documento preliminare di verifica assoggettabilità"/>)}
                            variables={{codice: uuid, tipo: VAS_DOCS.DOC_PRE_VER_VAS }}/>
                    </div>}
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked}
            getInput={getInputTipologia}
            mutation={UPDATE_VAS}
            value={VAS_TYPES.PROCEDIMENTO_SEMPLIFICATO}
            label={(<TextWithTooltip dataTip="art.8 co.5 L.R. 10/2010" text="PROCEDIMENTO SEMPLIFICATO"/>)}
            checked={tipologia === VAS_TYPES.PROCEDIMENTO_SEMPLIFICATO}
            className="mt-5 mb-4">
            {(checked) => <div className="row">
                <FileUpload {...fileProps}
                            disabled={!checked} isLocked={!checked || isLocked}
                            risorsa={docProcSemp}
                            placeholder={(<TextWithTooltip dataTip="art. 8, 22 e 23 L.R. 10/2010" text="Documento preliminare VAS"/>)}
                            variables={{codice: uuid, tipo: VAS_DOCS.DOC_PRE_VAS}}/>
                    </div>}
            </EnhancedSwitch>
        <EnhancedSwitch isLocked={isLocked}
            getInput={getInputTipologia}
            mutation={UPDATE_VAS}
            value={VAS_TYPES.PROCEDURA_ORDINARIA}
            checked={tipologia === VAS_TYPES.PROCEDURA_ORDINARIA}
            label={(<TextWithTooltip dataTip="FASE PRELIMINARE DI VAS (art.23 LR 10/2010)" text="PROCEDURA ORDINARIA DI VAS"/>)}
            className="mt-5">
            {() => (
                <div className="row">
                <span className="p-3 col-xl-12">Scegliendo “PROCEDURA ORDINARIA DI VAS” verrà inviata una comunicazione all’autorità procedente e proponente (AP/P)
            che avvierà le consultazioni degli Soggetti Competenti in Materia Ambientale (SCA)</span></div>

            )}
        </EnhancedSwitch>
        <EnhancedSwitch  isLocked={isLocked}
            getInput={getInputTipologia}
            mutation={UPDATE_VAS}
            value={VAS_TYPES.NON_NECESSARIA}
            checked={tipologia === VAS_TYPES.NON_NECESSARIA}
            label="VAS NON NECESSARIA"
            className="mt-5">
                {() =>(<div className="row"><span className="p-3 mb-5 col-xl-12">In questo caso per il piano non è necessaria alcuna VAS </span></div>)}
        </EnhancedSwitch>
        <div className="d-flex mt-2 pt-2 justify-content-between mb-3">
            <div style={{minWidth: "33%"}}>
                <Mutation mutation={UPDATE_PIANO} onError={showError}>
                {(onChange) => {
                        const changed = (val) => {
                            let soggettoProponenteUuid = val;
                            if(sP && sP.uuid === val){
                                soggettoProponenteUuid = null
                            }
                            onChange({variables:{ input:{
                                        pianoOperativo: { soggettoProponenteUuid}, codice}
                                }})
                        }
                        return (
                    <EnhancedListSelector
                            selected={sP ? [sP.uuid] : []}
                            query={GET_CONTATTI}
                            variables={{tipo: "opcom"}}
                            getList={getContatti}
                            label="DEFINISCI SOGGETTO PROPONENTE"
                            size="lg"
                            onChange={changed}
                            btn={(toggleOpen) => (<Button iconSize="icon-20" fontSize="size-11" disabled={isLocked} onClick={toggleOpen} className="my-auto text-uppercase" color="serapide" icon="add_circle" label="SOGGETTO PROPONENTE"></Button>)}
                        >
                        {/*<AddContact className="mt-2"
                         tipologia="generico"></AddContact>*/}
                        </EnhancedListSelector>
                        )}
                    }
                </Mutation>
                </div>
            <div style={{minWidth: "33%"}}>
                <Mutation mutation={UPDATE_PIANO} onError={showError}>
                {(onChange) => {
                    const changed = (val, {tipologia: qualifica, uuid}) => {
                        let newAC = acs.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid}))
                            newAC = newAC.filter(({ufficioUuid}) => uuid !== ufficioUuid)
                        if (newAC.length === acs.length){
                            newAC = [{qualifica, ufficioUuid: uuid}]
                            }
                        onChange({variables:{ input:{
                                    pianoOperativo: { soggettiOperanti: newAC.concat(scas.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid})))}, codice}
                            }})
                    }
                    return (
                        <EnhancedListSelector
                            selected={acs.map(({ufficio: {uuid} = {}}) => uuid)}
                            query={GET_CONTATTI}
                            getList={getContatti}
                            onChange={changed}
                            variables={{tipo: "ac"}}
                            size="lg"
                            label="SELEZIONA AUTORITA’ COMPETENTE VAS"
                            btn={(toggleOpen) => (<Button iconSize="icon-20" fontSize="size-11" disabled={isLocked} onClick={toggleOpen} className="text-uppercase" color="serapide" icon="add_circle" label="AUTORITA’ COMPETENTE VAS (AC)"/>)}
                            >
                            {/*<AddContact className="mt-2"
                             tipologia="acvas"></AddContact>*/}
                            </EnhancedListSelector>
                            )}
                }
                </Mutation>
            </div>
            <div style={{minWidth: "33%"}}>
                 <Mutation mutation={UPDATE_PIANO} onError={showError}>
            {(onChange) => {
                    const changed = (val, {tipologia: qualifica, uuid}) => {
                        let newSCA = scas.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid}))
                        
                        newSCA = newSCA.filter(({ufficioUuid}) => ufficioUuid !== uuid)
                        if (newSCA.length === scas.length) {
                            newSCA = newSCA.concat({qualifica, ufficioUuid: uuid})
                        }
                        onChange({variables:{ input:{
                                    pianoOperativo: { soggettiOperanti: newSCA.concat(acs.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid}) ))}, codice}
                            }})
                    }
                    return (
                <EnhancedListSelector
                        selected={scas.map(({ufficio: {uuid} = {}}) => uuid)}
                        query={GET_CONTATTI}
                        variables={{tipo: "sca"}}
                        getList={getContatti}
                        label="DEFINISCI SCA"
                        size="lg"
                        onChange={changed}
                        btn={(toggleOpen) => (<Button iconSize="icon-20" fontSize="size-11" onClick={toggleOpen} className="my-auto text-uppercase" disabled={disableSCA || isLocked} color="serapide" icon="add_circle" label="SOGGETTI COMPETENTI IN MATERIA AMBIENTALE (SCA)"></Button>)}
                    >
                    {/*<AddContact className="mt-2"
                     tipologia="sca"></AddContact>*/}
                    </EnhancedListSelector>
                )}
                }
                </Mutation>
            </div>
        </div>
        <div className="d-flex mt-5 pt-5  justify-content-end">
                <SalvaInvia mutation={PROMUOVI_PIANO} variables={{codice}} canCommit={canCommit}></SalvaInvia>
        </div>
    </React.Fragment>)})



export default ({codice, canUpdate, isLocked}) => {
    return (
        <Query query={GET_VAS} variables={{codice}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}} = {}}) => {
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
                return <UI codice={codice}  canUpdate={canUpdate} isLocked={isLocked} Vas={vas}/>
            }}
            </Query>)}
