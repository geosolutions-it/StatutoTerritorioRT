/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import UploadFiles from 'components/UploadFiles'
import Resource from 'components/Resource'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import RichiestaComune from 'components/RichiestaComune'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import  {showError, formatDate, getCodice, VAS_DOCS} from 'utils'

import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD, INVIO_PARERI_VERIFICA
} from 'schema'


const UI = ({
    back, 
    vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}} = {},
    utente: {fiscalCode} = {},
    azione: {scadenza, avvioScadenza} = {},
    tipo: tipoDoc = VAS_DOCS.PAR_VER_VAS,
    tipoVas = VAS_DOCS.DOC_PRE_VER_VAS,
    label = "PARERI",
    title = "Pareri SCA",
    saveMutation = INVIO_PARERI_VERIFICA}) => {
        
        const docsPareri =  resources.filter(({node: {tipo, user = {}}}) => tipo === tipoDoc && fiscalCode === user.fiscalCode).map(({node}) => node)
        const documento = resources.filter(({node: {tipo, user = {}}}) => tipo === tipoVas).map(({node}) => node).shift()
        
        return (
            <React.Fragment>
                <ActionTitle>{title}</ActionTitle>
                {avvioScadenza ? <RichiestaComune fontSize="size-11" iconSize="icon-15" scadenza={avvioScadenza}/> : <span className="pb-3"></span>}
                <Resource 
                iconSize="icon-15" fontSize="size-11" vertical useLabel
                className="border-0 mt-2" icon="attach_file" resource={documento}></Resource>
                <div className="mt-4 border-bottom-2 pb-3 d-flex">
                        <i className="material-icons text-serapide pr-3 icon-15">event_busy</i> 
                        <div className="d-flex flex-column size-11">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>{scadenza ? "Data entro la quale inviare i pareri" : "Nessuna data entro la quale inviare i pareri"}</span>
                        </div>
                </div>
                <ActionParagraphTitle fontWeight="font-weight-light">{label}</ActionParagraphTitle>
                <UploadFiles 
                        iconSize="icon-15" fontSize="size-11" vertical useLabel
                        risorse={docsPareri} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS}
                        variables={{codice: uuid, tipo: tipoDoc }}
                        isLocked={false}/>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={saveMutation} canCommit={docsPareri.length> 0}></SalvaInvia>
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
        