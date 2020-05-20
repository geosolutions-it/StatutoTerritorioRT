/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Resource from './Resource'
import TextWithTooltip from './TextWithTooltip'
import {isEmpty, map} from 'lodash'
import {formatDate, getNominativo, VAS_TYPES} from 'utils'

export default ({tipologia, docInizialeVAS = {}, pareriVerificaVAS = {}, provvedimentoVerifica = {}, assoggettamento, dataAssoggettamento }) => (
    <React.Fragment>
        <span className="pt-4">PERCORSO VAS SELEZIONATO:
            <span className="ml-3">
                {tipologia === VAS_TYPES.VERIFICA_SEMPLIFICATA && <TextWithTooltip className="font-weight-bold" dataTip="art.5 co.3ter L.R. 10/2010" text="PROCEDURA DI VERIFICA SEMPLIFICATA"/>}
                {tipologia === VAS_TYPES.VERIFICA && <TextWithTooltip className="font-weight-bold" dataTip="art.22 L.R. 10/2010" text="PROCEDURA DI VERIFICA DI ASSOGGETTABILITA’ A VAS"/>}
                {tipologia === VAS_TYPES.PROCEDIMENTO_SEMPLIFICATO && <TextWithTooltip className="font-weight-bold" dataTip="art.8 co.5 L.R. 10/2010" text="PROCEDIMENTO SEMPLIFICATO"/>}
                {tipologia === VAS_TYPES.PROCEDURA_ORDINARIA && <TextWithTooltip className="font-weight-bold" dataTip="FASE PRELIMINARE DI VAS (art.23 LR 10/2010)" text="PROCEDURA ORDINARIA DI VAS"/>}
                {tipologia === VAS_TYPES.NON_NECESSARIA && <span className="font-weight-bold">VAS NON NECESSARIA</span>}
            </span>
        </span>
        <div className="pl-2 pr-2">
            <div className="mt-4 mb-4">
                
                {tipologia !== VAS_TYPES.PROCEDURA_ORDINARIA && (
                <React.Fragment>
                    <TextWithTooltip className="mb-2 text-uppercase" dataTip={docInizialeVAS.tooltip} text={docInizialeVAS.label}></TextWithTooltip>  
                    <Resource  isLocked className="border-0 mt-2" icon="attach_file" resource={docInizialeVAS}/>
                </React.Fragment>    
                )}
                {!isEmpty(pareriVerificaVAS) && (
                    <div className="mt-4">
                        <div className="mb-2">PARERI DI VERIFICA VAS</div>
                        {map(pareriVerificaVAS, (u) => (
                            <div key={u[0].user.fiscalCode} className="mb-4">
                                <div className="d-flex text-serapide">
                                    <i className="material-icons">perm_identity</i>
                                    <span className="pl-2">{getNominativo(u[0].user)}</span>
                                </div>
                                {u.map(parere => (
                                    <Resource  fileSize={false} key={parere.uuid} className="border-0 mt-3" icon="attach_file" resource={parere}></Resource>
                                ))}
                            </div>
                        ))
                        }
                    </div>
                )}
                {!isEmpty(provvedimentoVerifica) && (
                    <div className="mt-4">
                        <div className="mb-2">PROVVEDIMENTO DI VERIFICA VAS</div>
                        <Resource isLocked className="mt-2" icon="attach_file" resource={provvedimentoVerifica}/>
                    </div>
                )}    
                {assoggettamento !== null && (
                    <div className="mt-4">
                        <span>ESITO VERIFICA ASSOGGETTAMENTO:
                            <span className="font-weight-bold ml-3 mr-3 text-serapide">
                            {assoggettamento ? "Assoggettamento VAS" : "Esclusione VAS"}
                            </span>
                            {!!dataAssoggettamento && <span>
                            il {formatDate(dataAssoggettamento)}
                            </span>}
                        </span>
                        
                    </div>
                    )
                }
            </div>
        </div>
    </React.Fragment>
)