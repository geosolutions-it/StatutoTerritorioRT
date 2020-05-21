/*
 * Copyright 2020, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from 'react'
import {Query, Mutation} from 'react-apollo'

import {UI as UploadFile} from './UploadFile';
import Spinner from 'components/Spinner'
import ListaContatti from 'components/ListaContatti'
import {EnhancedListSelector} from 'components/ListSelector'
import Button from 'components/IconButton'

import { 
    GET_VAS, VAS_FILE_UPLOAD, DELETE_RISORSA_VAS,
    UPDATE_PIANO, INVIO_DOC_PRELIMINARE, GET_CONTATTI
} from 'schema'


import  {showError, getCodice, getContatti} from 'utils'

const Action = ({modello, back, piano: {soggettiOperanti = [], codice} = {}}) =>  {
    
    const scas = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))
    const altri = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica !== "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))


    return (<UploadFile 
            back={back}
            title="Procedura VAS Ordinaria"
            placeholder="Documento preliminare VAS"
            fileType="documento_preliminare_vas"
            subTitle="Caricare il file del Documento preliminare VAS"
            deleteRes={DELETE_RISORSA_VAS} 
            uploadRes={VAS_FILE_UPLOAD}
            closeAction={INVIO_DOC_PRELIMINARE}
            modello={modello}
            >
            <ListaContatti title="SOGGETTI COMPETENTI SCA" contacts={scas}/>
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
                                </EnhancedListSelector>)
                        }
                    }
                </Mutation>
            </div>
            </UploadFile>)                                                                              
}



export default ({query, ...props}) => (
    <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
        {({loading, data: {modello: {edges: [modello] = []} = {}}}) => {
            if(loading) {
                return <Spinner/>
            }
            return (
                <Action {...props} modello={modello}/>)}
        }
    </Query>)