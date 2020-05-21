/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Query} from 'react-apollo';
import Resource from 'components/Resource'
import TextWithTooltip from 'components/TextWithTooltip'
import PercorsoVAS from 'components/PercorsoVAS'
import Spinner from 'components/Spinner'

import  {rebuildTooltip} from 'enhancers'
import {map, isEmpty}  from 'lodash'
import {getNominativo, showError, VAS_DOCS, docByVASType, filterAndGroupResourcesByUser, VAS_TYPES} from 'utils'

import { GET_VAS} from 'schema'




const UI = rebuildTooltip({onUpdate: false})(({codice, consultazioneSCA = {}, canUpdate, isLocked, Vas = {}}) => {
    
    const {node: {tipologia, dataAssoggettamento, assoggettamento, piano: {soggettiOperanti = [] } = {}, risorse : {edges: resources = []} = {}} = {}} = Vas
    
    
    const {node: docInizialeVAS} = resources.filter(({node: n}) => n.tipo === docByVASType[tipologia]).pop() || {};

    
    const {node: docProceduraVAS} = resources.filter(({node: n}) => n.tipo === VAS_DOCS.DOC_PRE_VAS).pop() || {};

    
    const acs = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "AC").map(({qualificaUfficio} = {}) => (qualificaUfficio))
    const scas = soggettiOperanti.filter(({qualificaUfficio: {qualifica} = {}} = {}) => qualifica === "SCA").map(({qualificaUfficio} = {}) => (qualificaUfficio))
    
    const pareriVerificaVAS =  filterAndGroupResourcesByUser( resources, VAS_DOCS.PAR_VER_VAS);
    const provvedimentoVerifica =  resources.filter(({node: {tipo}}) => tipo === VAS_DOCS.PROV_VER_VAS).map(({node}) => node).shift()
    
    const pareriSCA = filterAndGroupResourcesByUser( resources, VAS_DOCS.PAR_SCA)
    const pareriAC = resources.filter(({node: {tipo}}) => tipo === VAS_DOCS.PAR_AC).map(({node}) => node)
    
    const rapporto = resources.filter(({node: {tipo}}) => tipo === VAS_DOCS.RAPPORTO_AMBIENTALE).map(({node}) => node).shift()
    const sintesi = resources.filter(({node: {tipo}}) => tipo === VAS_DOCS.SINTESI_NON_TECNICA).map(({node}) => node).shift()

    return(
    <React.Fragment>
        <PercorsoVAS 
            tipologia={tipologia}
            docInizialeVAS={docInizialeVAS}
            pareriVerificaVAS={pareriVerificaVAS}
            provvedimentoVerifica={provvedimentoVerifica}
            assoggettamento={assoggettamento}
            dataAssoggettamento={dataAssoggettamento}
        />
        {(assoggettamento || tipologia === VAS_TYPES.PROCEDURA_ORDINARIA) && (
            <div className="mt-6">
            <span >PROCEDURA VAS FASE PRELIMINARE art. 23</span>
                <div className="pl-2 pr-2">
                    <div className="mt-4 mb-4">
                        <TextWithTooltip className="mb-2 text-uppercase" dataTip={docProceduraVAS.tooltip} text={docProceduraVAS.label}></TextWithTooltip>  
                        <Resource isLocked className="mt-2" icon="attach_file" resource={docProceduraVAS}/>
                        {!isEmpty(pareriSCA) && (
                            <div className="mt-4">
                                <div className="mb-2">PARERI VAS SCA</div>
                                {map(pareriSCA, (u) => (
                                    <div key={u[0].user.fiscalCode} className="mb-4">
                                        <div className="d-flex text-serapide">
                                            <i className="material-icons">perm_identity</i>
                                            <span className="pl-2">{getNominativo(u[0].user)}</span>
                                        </div>
                                        {u.map(parere => (
                                            <Resource fileSize={false} key={parere.uuid} className="border-0 mt-3" icon="attach_file" resource={parere}></Resource>
                                        ))}
                                    </div>
                                ))
                                }
                            </div>)}
                        {pareriAC.length > 0 && (
                        <div className="mt-4">
                            <div className="mb-2">PARERI VAS AC</div>
                            {pareriAC.map((parere) => (
                                <Resource fileSize={false} key={parere.uuid} className="border-0 mt-3" icon="attach_file" resource={parere}></Resource>
                            ))
                            }
                        </div>
                        )}
                        {(!isEmpty(rapporto)  || !isEmpty(sintesi)) && (<div className="mt-4">
                            <div className="mb-2">DOCUMENTI VAS</div>
                            <Resource useLabel isLocked className="mt-2" icon="attach_file" resource={rapporto}/>
                            <Resource useLabel isLocked className="mt-2" icon="attach_file" resource={sintesi}/>
                        </div>)}
                    </div>
                </div>
            </div>
        )}
        <div className="d-flex mt-6 pt-2 justify-content-between mb-3">
            <div style={{minWidth: "30%"}}>
                <span>AUTORITA’ COMPETENTE VAS</span>
                {acs.length > 0 ? acs.map(({ufficio: {nome, uuid, ente: {nome: nomeEnte} = {}} = {}}) => (
                    <div className="d-flex pt-3" key={uuid}>
                        <i className="material-icons text-serapide">bookmark</i>
                        {`${nomeEnte} ${nome}`}
                    </div>
                    )) : (
                    <div className="d-flex pt-3">AC non selezionato</div>
                    )
                }
            </div>
            <div style={{minWidth: "60%"}}>
                <span>SOGGETTI COMPETENTI IN MATERIA AMBIENTALE</span>
                {scas.length >0 ? scas.map(({ufficio: {nome, uuid, ente: {nome: nomeEnte} = {}} = {}}) => (
                    <div className="d-flex pt-3" key={uuid}>
                        <i className="material-icons text-serapide">bookmark</i>
                        {`${nomeEnte} ${nome}`}
                    </div>)) : (
                        <div className="d-flex pt-3">Soggeti SCA non selezionati</div>
                    )
                }
            </div>
        </div>
    </React.Fragment>)})



export default ({codice, canUpdate, isLocked}) => {
    return (
        <Query query={GET_VAS} variables={{codice}} onError={showError}>
            {({loading, data: {modello: {edges: [vas] = []} = {}} = {}}) => {
                return loading? <Spinner/> : <UI codice={codice} canUpdate={canUpdate} isLocked={isLocked} Vas={vas}/>
                }
            }
        </Query>
        )}    
    
