/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from "react-apollo"

import FileUpload from 'components/UploadSingleFile'
import {EnhancedSwitch} from 'components/Switch'
import AutoMutation from 'components/AutoMutation'
import Resource from 'components/Resource'
import {EnhancedListSelector} from 'components/ListSelector'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
// import AddContact from 'components/AddContact'
import Button from 'components/IconButton'
import RichiestaComune from 'components/RichiestaComune'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import ListaContatti from 'components/ListaContatti'


import {rebuildTooltip} from 'enhancers'
import  {showError, formatDate, getInputFactory, getCodice, getContatti} from 'utils'

import {GET_CONSULTAZIONE_VAS, CREA_CONSULTAZIONE_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD,
    UPDATE_CONSULTAZIONE_VAS,
    AVVIO_CONSULTAZIONE_VAS, UPDATE_PIANO,
    GET_CONTATTI
} from 'schema'

const getConsultazioneVasTypeInput = getInputFactory("consultazioneVas")

const UI = rebuildTooltip()(({
    consultazioneSCA: { node: {
        avvioConsultazioniSca,
        dataCreazione,
        dataRicezionePareri,
        proceduraVas: {uuid: pVasUUID, dataAssoggettamento, tipologia, risorse: {edges=[]} = {} } = {},
        uuid} = {}} = {},
        piano: {
            codice,
            autoritaCompetenteVas: {edges: aut =[]} = {},
            soggettiSca: {edges: sca = []} = {}} = {}, back}) => {

            const isFull = tipologia === "SEMPLIFICATA" || tipologia === "VERIFICA"
            const provvedimentoVerificaVas  = edges.filter(({node: {tipo}}) => tipo === "provvedimento_verifica_vas").map(({node}) => node).shift()
            const docPrelim = edges.filter(({node: {tipo}}) => tipo === "documento_preliminare_vas").map(({node}) => node).shift()
            const auths = aut.map(({node: {uuid} = {}} = {}) => uuid)
            const scas = sca.map(({node: {uuid} = {}} = {}) => uuid)
            const getInput = getConsultazioneVasTypeInput(uuid, "avvioConsultazioniSca")
            return (<React.Fragment>
                <ActionTitle>Avvio Consultazioni SCA</ActionTitle>
                {isFull ? (<React.Fragment>
                    <div className="py-3 border-bottom">
                        <Resource iconSize="icon-15" fontSize="size-11" vertical useLabel className="border-0 mt-4" icon="attach_file" resource={provvedimentoVerificaVas}></Resource>
                        <div className="row mt-4 size-11">
                            <div className="col-6 d-flex">
                                <i className="material-icons text-serapide icon-15 self-align-center">assignment_turned_in</i>
                                <span className="pl-1 ">ESITO: Assoggettamento VAS</span>
                            </div>
                            <span className="col-3">{dataAssoggettamento && formatDate(dataAssoggettamento)}</span>
                        </div>
                    </div>
                    <ListaContatti title="AUTORITA' COMPETENTE (AC)" contacts={aut}></ListaContatti>
                    <div className="mt-3 pl-4 ">
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
                                    getList={getContatti}
                                    onChange={changed}
                                    variables={{tipo: "acvas"}}
                                    size="lg"
                                    btn={(toggleOpen) => (
                                        <div className="row">
                                            <Button fontSize="size-8"  iconSize="icon-13"  classNameLabel="py-0" onClick={toggleOpen} className="text-serapide rounded-pill" color="dark" icon="add_circle" label="Autorità competente VAS (AC)"/>
                                        </div>
                                        )}

                                    >
                                    {/*<AddContact className="mt-2"
                                     tipologia="acvas"></AddContact>*/}
                                    </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                        <ListaContatti title="SOGGETTI COMPETENTI SCA" contacts={sca}></ListaContatti>
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
                                onChange={changed}
                                getList={getContatti}
                                label="DEFINISCI SCA"
                                size="lg"
                                btn={(toggleOpen) => (
                                    <div className="row">
                                        <Button
                                            fontSize="size-8"  iconSize="icon-13"
                                            classNameLabel="py-0"
                                            onClick={toggleOpen}
                                            className="text-serapide rounded-pill"
                                            color="dark" icon="add_circle"
                                            label="Soggetti competenti in materia ambientale (SCA)"/>
                                    </div>)}
                            >
                            {/*<AddContact className="mt-2"
                             tipologia="sca"></AddContact>*/}
                            </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                    </React.Fragment>
                    ) : (
                        <RichiestaComune  fontSize="size-11" iconSize="icon-15" scadenza={dataCreazione}/>
                        )}

                <ActionParagraphTitle fontWeight="font-weight-light">DOCUMENTO PRELIMINARE</ActionParagraphTitle>
                <div className="action-uploader  py-1 align-self-start">
                <FileUpload
                    iconSize="icon-15" fontSize="size-11" vertical useLabel
                    className={`border-0 ${!docPrelim ? "flex-column": ""}`}
                    sz="sm" modal={false} showBtn={false}
                    mutation={VAS_FILE_UPLOAD}
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false}
                    isLocked={false} risorsa={docPrelim} variables={{codice: pVasUUID, tipo: "documento_preliminare_vas" }}/>
                </div>

                    <div className="row pt-4 pl-0 ">
                        <div className="col-7 d-flex align-items-center switch-small ">
                            <i className="material-icons text-serapide icon-15 pr-2">email</i>
                            <div className="bg-serapide px-2 size-12">Avvia consultazione SCA</div>
                            <EnhancedSwitch value={!avvioConsultazioniSca}
                                getInput={getInput}
                                ignoreChecked
                                labelClassName="col-auto"
                                mutation={UPDATE_CONSULTAZIONE_VAS} checked={avvioConsultazioniSca}
                            />
                        </div>
                        <div className="col-5 d-flex align-items-center">
                            <i className="material-icons icon-15 pr-2">event_busy</i>
                            <div className="d-flex flex-column size-10">
                                <span>{dataRicezionePareri && formatDate(dataRicezionePareri, "dd MMMM yyyy")}</span>
                                <span>90 giorni per ricevere i pareri sca</span>
                            </div>
                        </div>
                        <div className="col-8 pt-3 text-justify pr-2 size-13">Selezionando l’opzione e cliccando “Salva e Invia” verrà inviata comunicazione e
                            documento preliminare agli SCA selezionati e per conoscenza all’Autorità Competente
                            in materia ambientale identificati all’atto di creazione del Piano.</div>
                      </div>



                <div className="align-self-center mt-7">
                <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={AVVIO_CONSULTAZIONE_VAS} canCommit={avvioConsultazioniSca && docPrelim && (!isFull || (auths.length > 0 && scas.length > 0))}></SalvaInvia>

                </div>
            </React.Fragment>)})

const updateCache =(codice) => (cache, { data: {createConsultazioneVas : { nuovaConsultazioneVas: node}}  = {}} = {}) => {
    if (node) {
        const consultazioneVas = {__typename: "ConsultazioneVASNodeConnection", edges: [{__typename: "ConsultazioneVASNodeEdge", node}]}
        cache.writeQuery({
                        query: GET_CONSULTAZIONE_VAS,
                        data: { modello: consultazioneVas},
                        variables: {codice}
                    })
    }
}
export default (props) => {
        const codice = getCodice(props)
        return (
                <Query query={GET_CONSULTAZIONE_VAS} variables={{codice}} onError={showError}>
                    {({loading, data: {modello: {edges: [consultazioneSCA] = []} = []} = {}, error}) => {
                        if (!loading && !error && !consultazioneSCA && codice) {
                            return (
                                <AutoMutation variables={{input: {codicePiano: codice}}} mutation={CREA_CONSULTAZIONE_VAS} onError={showError} update={updateCache(codice)}>
                                    {() => (
                                        <div className="flex-fill d-flex justify-content-center">
                                            <div className="spinner-grow " role="status">
                                                <span className="sr-only">Loading...</span>
                                            </div>
                                        </div>)}
                                </AutoMutation>)
                        }
                        if(loading) {
                            return <Spinner/>
                        }
                        return (
                            <UI {...props} consultazioneSCA={consultazioneSCA}/>)}
                    }
                </Query>)
    }
