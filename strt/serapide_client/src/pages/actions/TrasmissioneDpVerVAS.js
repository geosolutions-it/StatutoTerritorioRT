/*
 * Copyright 2020, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from 'react-apollo'

import Resource from 'components/Resource'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import RichiestaComune from 'components/RichiestaComune'
import ListaContatti from 'components/ListaContatti'
import {EnhancedListSelector} from 'components/ListSelector'
//import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Button from 'components/IconButton'
import Spinner from 'components/Spinner'

import  {showError, formatDate, daysSub, getCodice, getContatti, VAS_DOCS} from 'utils'

import {GET_VAS, 
    TRASMISSIONE_DPV_VAS,
    GET_CONTATTI,
    UPDATE_PIANO
} from 'schema'


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    scadenza,
    piano: {soggettiOperanti = [], codice} = {},
    saveMutation = TRASMISSIONE_DPV_VAS}) => {
        
        const dpvevass = resources.filter(({node: {tipo, user = {}}}) => tipo === VAS_DOCS.DOC_PRE_VER_VAS).map(({node}) => node).shift()
        const scas = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))
        const altri = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica !== "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))
        return (
            <React.Fragment>
                <ActionTitle>Trasmissione Documento Preliminare Verifica VAS</ActionTitle>
                <RichiestaComune fontSize="size-11" iconSize="icon-15" scadenza={scadenza && daysSub(scadenza, 30)}/>
                <Resource 
                iconSize="icon-15" fontSize="size-11" vertical useLabel
                className="border-0 mt-2" icon="attach_file" resource={dpvevass}></Resource>
                <div className="mt-4 border-bottom-2 pb-3 d-flex">
                        <i className="material-icons text-serapide pr-3 icon-15">event_busy</i> 
                        <div className="d-flex flex-column size-11">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <ListaContatti title="SOGGETTI COMPETENTI SCA" contacts={scas}></ListaContatti>
                    <div className="mt-3 pl-4 border-bottom-2 pb-5">
                    <Mutation mutation={UPDATE_PIANO} onError={showError}>
                    {(onChange) => {
                        const changed = (val, {tipologia: qualifica, uuid}) => {
                            let newSCA = scas.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid}))
                            
                            newSCA = newSCA.filter(({ufficioUuid}) => ufficioUuid !== uuid)
                            if (newSCA.length === scas.length) {
                                newSCA = newSCA.concat({qualifica, ufficioUuid: uuid})
                            }
                            onChange({variables:{ input:{
                                        pianoOperativo: { soggettiOperanti: newSCA.concat(altri.map(({qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}) => ({qualifica, ufficioUuid}) ))}, codice}
                                }})
                        }
                            return (
                        <EnhancedListSelector
                                selected={scas.map(({ufficio: {uuid} = {}}) => uuid)}
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
                            </EnhancedListSelector>)}
                        }
                        </Mutation>
                        </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{uuid}} mutation={saveMutation} canCommit={scas.length > 0}></SalvaInvia>
                </div>
            </React.Fragment>)
    }
export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas}  />)}
            }
        </Query>)