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

import {rebuildTooltip} from 'enhancers'
import {map} from 'lodash'
import  {showError, formatDate,daysSub, getNominativo, filterAndGroupResourcesByUser, getCodice} from 'utils'

import {GET_VAS,
    DELETE_RISORSA_VAS,
    VAS_FILE_UPLOAD,
    UPDATE_VAS,
    PROVVEDIMENTO_VERIFICA_VAS
} from 'schema'



const SwitchAssoggetamento = ({uuid, assoggettamento}) => (
        <Mutation mutation={UPDATE_VAS} onError={showError}>
            {(update) => {
                const onClick = (val) =>{
                    if(val !== assoggettamento) {
                        update({variables: {input: {proceduraVas: {assoggettamento: !assoggettamento}, uuid}}})
                    }
                }
                return (
                    <div className="d-flex mt-3 mb-5 justify-content-around">
                        <span className="d-flex justify-content-start pointer">
                            <i className={`material-icons text-serapide icon-34 ${!assoggettamento ? '' : 'pointer'}`} onClick={() => onClick(false)}>{assoggettamento ? 'radio_button_unchecked' : 'radio_button_checked'}</i>
                            <span className="pl-2 align-self-center">esclusione da VAS</span>
                        </span>
                        <span className="d-flex justify-content-start pointer">
                            <i className={`material-icons text-serapide icon-34 ${assoggettamento ? '' : 'pointer'}`} onClick={() =>  onClick(true)}>{!assoggettamento ? 'radio_button_unchecked' : 'radio_button_checked'}</i>
                            <span className="pl-2 align-self-center">assoggetamento VAS</span>
                        </span>
                    </div>)
            }}
        </Mutation>
)




const UI = rebuildTooltip()(({
    back,
    vas: {node: {uuid, assoggettamento, relazioneMotivataVasSemplificata, documentoPreliminareVerifica, tipologia, risorse : {edges: resources = []} = {}} = {}} = {},
    scadenza}) => {
    
        const IsSemplificata = tipologia === 'SEMPLIFICATA';
        const pareriUser =  filterAndGroupResourcesByUser( resources, "parere_verifica_vas")
    
        

        const provvedimento =  resources.filter(({node: {tipo}}) => tipo === "provvedimento_verifica_vas").map(({node}) => node).shift()
        return (
            <React.Fragment>
                <ActionTitle><TextWithTooltip text="Provvedimento di Verifica" dataTip="art.22 L.R. 10/2010"/></ActionTitle>
                <RichiestaComune scadenza={scadenza && daysSub(scadenza, IsSemplificata ? 30 : 90)}/>
                <Resource className="border-0 mt-2" icon="attach_file" resource={IsSemplificata ? relazioneMotivataVasSemplificata : documentoPreliminareVerifica}></Resource>
                <div className="mt-3 mb-5 border-bottom-2 pb-2 d-flex">
                        <i className="material-icons text-serapide pr-3">event_busy</i> 
                        <div className="d-flex flex-column">
                            <span>{scadenza && formatDate(scadenza, "dd MMMM yyyy")}</span>
                            <span>Data entro la quale ricevere i pareri</span>
                        </div>
                </div>
                <div className={className(" mb-4", {"border-bottom-2": pareriUser.length > 0})}>
                {map(pareriUser, (u) => (
                    <div key={u[0].user.fiscalCode} className="mb-4">
                        <div className="d-flex text-serapide"><i className="material-icons">perm_identity</i><span className="pl-2">{getNominativo(u[0].user)}</span></div>
                        {u.map(parere => (<Resource key={parere.uuid} className="border-0 mt-2" icon="attach_file" resource={parere}></Resource>))}
                    </div>
                    ))
                    }
                </div>
                <h4>Emissione Provvedimento di Verifica</h4> 
                <SwitchAssoggetamento assoggettamento={assoggettamento} uuid={uuid}></SwitchAssoggetamento>
                <h4 className="font-weight-light pl-4 pb-1">PROVVEDIMENTO DI VERIFICA</h4>
                    <div className="action-uploader  align-self-start pb-5">
                    <FileUpload 
                        className={`border-0 ${!provvedimento ? "flex-column": ""}`}
                        sz="sm" modal={false} showBtn={false} 
                        mutation={VAS_FILE_UPLOAD} 
                        resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                        isLocked={false} risorsa={provvedimento} variables={{codice: uuid, tipo: "provvedimento_verifica_vas" }}/>
                    </div>
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} mutation={PROVVEDIMENTO_VERIFICA_VAS} variables={{uuid}} canCommit={!!provvedimento}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
    <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
        {({loading, data: {modello: {edges: [vas] = []} = {}} = {}}) => {
            if(loading) {
                return (
                    <div className="flex-fill d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>)
            }
            return (
                <UI {...props} vas={vas}/>)}
        }
    </Query>)