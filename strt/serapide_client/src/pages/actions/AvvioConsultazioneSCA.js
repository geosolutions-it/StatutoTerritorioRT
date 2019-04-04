/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import FileUpload from '../../components/UploadSingleFile'
import  {showError, formatDate} from '../../utils'
import {EnhancedSwitch} from '../../components/Switch'
import AutoMutation from '../../components/AutoMutation'
import {Query, Mutation} from "react-apollo"
import Resource from '../../components/Resource'
import {EnhancedListSelector} from '../../components/ListSelector'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import AddContact from '../../components/AddContact'
import Button from '../../components/IconButton'
import RichiestaComune from '../../components/RichiestaComune'
import {GET_CONSULTAZIONE_VAS, CREA_CONSULTAZIONE_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD,
    UPDATE_CONSULTAZIONE_VAS,
    AVVIO_CONSULTAZIONE_VAS, UPDATE_PIANO,
    GET_CONTATTI
} from '../../queries'




const getSuccess = ({uploadRisorsaVas: {success}} = {}) => success
const getVasTypeInput = (uuid) => (value) => ({
    variables: {
        input: { 
            consultazioneVas: {avvioConsultazioniSca:!value}, 
            uuid
        }
    }
})
const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid}}) => ({label: nome, value: uuid}))
}

const UI = ({consultazioneSCA: {node: {avvioConsultazioniSca, dataCreazione, dataRicezionePareri, dataScadenza, proceduraVas: {uuid: pVasUUID, dataAssoggettamento, tipologia, risorse: {edges=[]} = {} } = {}, uuid} = {}} = {}, piano: {codice, autoritaCompetenteVas: {edges: aut =[]} = {}, soggettiSca: {edges: sca = []} = {}} = {}, back}) => {
            
            const isFull = tipologia === "SEMPLIFICATA" || tipologia === "VERIFICA"
            const provvedimentoVerificaVas  = edges.filter(({node: {tipo}}) => tipo === "provvedimento_verifica_vas").map(({node}) => node).shift()
            const docPrelim = edges.filter(({node: {tipo}}) => tipo === "documento_preliminare_vas").map(({node}) => node).shift()
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const scas = sca.map(({node: {uuid} = {}} = {}) => uuid)
            return (<React.Fragment>
                <ActionTitle>Avvio Consultazioni SCA</ActionTitle>
                {isFull ? (<React.Fragment>
                    <div className="py-3 border-bottom-2">
                        <Resource className="border-0 mt-2" icon="attach_file" resource={provvedimentoVerificaVas}></Resource>
                        <div className="row mt-2">
                            <div className="col-6 d-flex">
                                <i className="material-icons text-serapide self-align-center">assignment_turned_in</i>
                                <span className="pl-1">ESITO: Assoggettamento VAS</span>
                            </div>
                            <span className="col-3">{dataAssoggettamento && formatDate(dataAssoggettamento)}</span>
                        </div>
                    </div>
                    <h5 className="font-weight-light pb-1 mt-3">AUTORITA' COMPETENTE (AC)</h5>
                    {aut.map(({node: {nome, uuid} = {}}) => (<div className="d-flex pl-2 mt-3 " key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                    <div className="mt-4 pl-4 pb-4">
                    <Mutation mutation={UPDATE_PIANO} onError={showError}>
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
                                    btn={(toggleOpen) => (
                                        <div className="row">
                                            <Button fontSize="60%"  classNameLabel="py-0" onClick={toggleOpen} className="text-serapide rounded-pill" color="dark" icon="add_circle" label="Autorità competente VAS (AC)"/>
                                        </div>
                                        )}

                                    >
                                    <AddContact className="mt-2" tipologia="acvas"></AddContact>
                                    </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <h5 className="font-weight-light pb-1 mt-3">SOGGETTI COMPETENTI SCA</h5>
                        {sca.map(({node: {nome, uuid} = {}}) => (<div className="d-flex mt-3" key={uuid}>
                                 <i className="material-icons text-serapide">bookmark</i>
                                 {nome}
                        </div>))}
                        <div className="mt-3 pl-4 border-bottom-2 pb-5">
                        <Mutation mutation={UPDATE_PIANO} onError={showError}>
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
                                btn={(toggleOpen) => (
                                    <div className="row">
                                        <Button 
                                            fontSize="60%"  
                                            classNameLabel="py-0" 
                                            onClick={toggleOpen} 
                                            className="text-serapide rounded-pill" 
                                            color="dark" icon="add_circle" 
                                            label="Soggetti competenti in materia ambientale (SCA)"/>
                                    </div>)}
                            >
                            <AddContact className="mt-2" tipologia="sca"></AddContact>
                            </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                    </React.Fragment>
                    ) : (
                        <RichiestaComune   scadenza={dataCreazione}/> 
                        )}
                
                <h4 className="font-weight-light pt-4 pl-2 pb-1">DOCUMENTO PRELIMINARE</h4>
                <div className="action-uploader  align-self-start pl-2 pb-5">
                <FileUpload 
                    className={`border-0 ${!docPrelim ? "flex-column": ""}`}
                    sz="sm" modal={false} showBtn={false} 
                    getSuccess={getSuccess} mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>
                
                    <div className="row pl-2">
                        <div className="col-8">
                            <div className="col-12 d-flex pl-0">
                                <i className="material-icons text-serapide pr-3">email</i>
                                <div className="bg-serapide mb-auto px-2">Avvia consultazione SCA</div>
                                <EnhancedSwitch value={avvioConsultazioniSca}
                                    getInput={getVasTypeInput(uuid)}  
                                    ignoreChecked
                                    mutation={UPDATE_CONSULTAZIONE_VAS} checked={avvioConsultazioniSca} 
                                /> 
                            </div>
                            
                            <div className="col-12 pt-2">Selezionando l’opzione e cliccando “Salva e Invia” verrà inviata comunicazione e
                            documento preliminare agli SCA selezionati e per conoscenza all’Autorità Competente
                            in materia ambientale identificati all’atto di creazione del Piano.</div>
                        
                        </div>
                        <div className="col-4 d-flex">
                            <i className="material-icons pr-3">event_busy</i> 
                            <div className="d-flex flex-column">
                                <span>{dataRicezionePareri && formatDate(dataRicezionePareri, "dd MMMM yyyy")}</span>
                                <span style={{maxWidth: 150}}>90 giorni per ricevere i pareri sca</span>
                            </div>
                        </div>
                      </div> 
                    
                    
                
                <div className="align-self-center mt-7">
                <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={AVVIO_CONSULTAZIONE_VAS} canCommit={avvioConsultazioniSca && docPrelim && (!isFull || (auths.length > 0 && scas.length > 0))}></SalvaInvia>
                
                </div>
            </React.Fragment>)}

const updateCache =(codice) => (cache, { data: {createConsultazioneVas : { nuovaConsultazioneVas: node}}  = {}} = {}) => {
    if (node) {
        const consultazioneVas = {__typename: "ConsultazioneVASNodeConnection", edges: [{__typename: "ConsultazioneVASNodeEdge", node}]}
        cache.writeQuery({
                        query: GET_CONSULTAZIONE_VAS,
                        data: { consultazioneVas},
                        variables: {codice}
                    })
    }
}
export default ({codicePiano, back, piano}) => (
                <Query query={GET_CONSULTAZIONE_VAS} variables={{codice: codicePiano}} onError={showError}>
                    {({loading, data: {consultazioneVas: {edges = []} = []} = {}, error}) => {
                        if (!loading && !error && edges.length === 0 && codicePiano) {
                            return (
                                <AutoMutation variables={{input: {codicePiano}}} mutation={CREA_CONSULTAZIONE_VAS} onError={showError} update={updateCache(codicePiano)}>
                                    {() => (
                                        <div className="flex-fill d-flex justify-content-center">
                                            <div className="spinner-grow " role="status">
                                                <span className="sr-only">Loading...</span>
                                            </div>
                                        </div>)}
                                </AutoMutation>)
                        }
                        if(loading) {
                            return (
                                <div className="flex-fill d-flex justify-content-center">
                                    <div className="spinner-grow " role="status">
                                        <span className="sr-only">Loading...</span>
                                    </div>
                                </div>)
                        }
                        return (
                            <UI consultazioneSCA={edges[0]} back={back} piano={piano}/>)}
                    }
                </Query>)