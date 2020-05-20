/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from 'react-apollo'

import FileUpload from 'components/UploadSingleFile'
import Resource from 'components/Resource'
import RichiestaComune from 'components/RichiestaComune'
import SalvaInvia from 'components/SalvaInvia'
import className from "classnames"
import ActionTitle from 'components/ActionTitle'
import TextWithTooltip from 'components/TextWithTooltip'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import Spinner from 'components/Spinner'

import {rebuildTooltip} from 'enhancers'
import {map} from 'lodash'
import  {showError, formatDate, getNominativo, filterAndGroupResourcesByUser, getCodice, docByVASType , VAS_DOCS} from 'utils'

import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD,
    UPDATE_VAS,
    EMISSIONE_PROVVEDIMENTO_VERIFICA_VAS
} from 'schema'



const SwitchAssoggettamento = ({uuid, assoggettamento, fontSize, iconSize = "icon-34"}) => (
        <Mutation mutation={UPDATE_VAS} onError={showError}>
            {(update) => {
                const onClick = (val) =>{
                    if(val !== assoggettamento) {
                        update({variables: {input: {proceduraVas: {assoggettamento: val}, uuid}}})
                    }
                }
                return (
                    <div className="d-flex mt-3 justify-content-around">
                        <span className="d-flex justify-content-start pointer">
                            <i className={`material-icons text-serapide ${iconSize} ${assoggettamento === false ? 'pointer': ''}`} onClick={() => onClick(false)}>{assoggettamento === false ? 'radio_button_checked' : 'radio_button_unchecked'}</i>
                            <span className={`pl-2 align-self-center ${fontSize}`}>esclusione da VAS</span>
                        </span>
                        <span className="d-flex justify-content-start pointer">
                            <i className={`material-icons text-serapide ${iconSize} ${assoggettamento === true ? 'pointer' : ''}`} onClick={() =>  onClick(true)}>{assoggettamento === true ? 'radio_button_checked' : 'radio_button_unchecked' }</i>
                            <span className={`pl-2 align-self-center ${fontSize}`}>assoggettamento VAS</span>
                        </span>
                    </div>)
            }}
        </Mutation>
)




const UI = rebuildTooltip()(({
    back,
    vas: {node: {uuid, assoggettamento, tipologia, risorse : {edges: resources = []} = {}} = {}} = {},
    azione: {scadenza, avvioScadenza} = {}}) => {
    
        
        const pareriUser =  filterAndGroupResourcesByUser( resources, VAS_DOCS.PAR_VER_VAS)
        
        const provvedimento =  resources.filter(({node: {tipo}}) => tipo === VAS_DOCS.PROV_VER_VAS).map(({node}) => node).shift()
        
        
        const risorsa = resources.filter(({node: {tipo}}) => tipo === docByVASType[tipologia]).map(({node}) => node).shift() 


        return (
            <React.Fragment>
                <ActionTitle><TextWithTooltip text="Provvedimento di Verifica" dataTip="art.22 L.R. 10/2010"/></ActionTitle>
                <RichiestaComune iconSize="icon-15" fontSize="size-11" scadenza={avvioScadenza}/>  
                <Resource useLabel iconSize="icon-15" fileSize={false} fontSize="size-11"  className="border-0 mt-3" icon="attach_file" resource={risorsa}></Resource>
                <div className="mt-4 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3 icon-15">event_busy</i> 
                        <div className="d-flex flex-column size-11">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data massima entro la quale inviare il provvedimento di verifica</span>
                        </div>
                </div>
                <div className={className(" mt-4", {"border-bottom-2": pareriUser.length > 0})}>
                {map(pareriUser, (u) => (
                    <div key={u[0].user.fiscalCode} className="mb-4">
                        <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                        {u.map(parere => (<Resource useLabel iconSize="icon-15" fileSize={false} fontSize="size-11" key={parere.uuid} className="border-0 mt-3" icon="attach_file" resource={parere}></Resource>))}
                    </div>
                    ))
                    }
                </div>
                <ActionParagraphTitle>Emissione Provvedimento di Verifica</ActionParagraphTitle> 
                <SwitchAssoggettamento fontSize="size-11" iconSize="icon-15" assoggettamento={assoggettamento} uuid={uuid}></SwitchAssoggettamento>
                <ActionParagraphTitle fontWeight="font-weight-light">PROVVEDIMENTO DI VERIFICA</ActionParagraphTitle>
                    <div className="action-uploader  py-1 align-self-start border-bottom">
                    <FileUpload 
                        iconSize="icon-15" fontSize="size-11" vertical useLabel
                        className={`border-0 ${!provvedimento ? "flex-column": ""}`}
                        sz="sm" modal={false} showBtn={false} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                        isLocked={false} risorsa={provvedimento} variables={{codice: uuid, tipo:VAS_DOCS.PROV_VER_VAS}}/>
                    </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} mutation={EMISSIONE_PROVVEDIMENTO_VERIFICA_VAS} variables={{uuid}} canCommit={!!provvedimento && assoggettamento !== null}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
    <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
        {({loading, data: {modello: {edges: [vas] = []} = {}} = {}}) => {
            if(loading) {
                return <Spinner/>
            }
            return (
                <UI {...props} vas={vas}/>)}
        }
    </Query>)