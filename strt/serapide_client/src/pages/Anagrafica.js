/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import { toast } from 'react-toastify'

import {Query} from "react-apollo"
import {getEnteLabelID} from "utils"
import {GET_PIANI} from "schema"

import {formatDate} from "utils"

import Risorsa from 'components/Resource'
import VAS from 'components/VAS'
import PianoPageContainer from 'components/PianoPageContainer';
import PianoSubPageTitle from '../components/PianoSubPageTitle';



export default ({match: {params: {code} = {}} = {}, ...props}) => {
    return (<Query query={GET_PIANI} variables={{codice: code}}>
        {({loading, data: {piani: {edges: [piano] = []} = {}} = {}, error}) => {
            if(loading){
                return (
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
            } else if(!piano) {
                toast.error(`Impossobile trovare il piano: ${code}`,  {autoClose: true})
                return <div></div>
            }
            const {node: {ente, fase: {nome: faseNome}, risorse : {edges: resources = []} = {}, codice = "", dataDelibera, numeroDelibera} = {}} = piano
            const locked = faseNome !== "DRAFT"
            const {node: delibera} = resources.filter(({node: n}) => n.tipo === "delibera").pop() || {};
            let optionals = resources.filter(({node: n}) => n.tipo === "delibera_opts").map(({node}) => (node) ) || [];
            if(!locked) {
                window.location.href=`#/crea_anagrafica/${code}`
            }
            
            return(
                    <PianoPageContainer>
                        <PianoSubPageTitle icon="assignment" title="ANAGRAFICA"/>
                            <div className="d-flex flex-column flex-fill">
                                <div className="pt-5 row">
                                    <div className="col-12 py-2">ID {getEnteLabelID(ente)}</div>
                                    <div className="col-12 py-2 pt-4">DELIBERA DEL {formatDate(dataDelibera)}  &nbsp; N° {numeroDelibera ?? "N° delibera non selezionato"}</div>
                                    <div className="col-12 py-2">
                                    <Risorsa fileSize={false} useLabel resource={delibera} isLocked/> </div>
                                
                                <div className="col-12 pt-4 pb2">ALTRI DOCUMENTI	
                                {optionals.length > 0 ? optionals.map(doc => (	
                                    <div key={doc.uuid} className="col-12 py-2">	
                                        <Risorsa fileSize={false}  resource={doc} isLocked={true}/> 	
                                    </div>)): (<div className="col-12 px-0 py-2">Nessun allegato presente</div>)}
                                </div>
                                </div>
                                <div style={{borderBottom: "2px dashed"}} className="mt-5 text-serapide" ></div>
                                <VAS codice={codice} canUpdate={false} isLocked={locked}></VAS>
                            </div>  
                    </PianoPageContainer>
                   
            )}
        }
    </Query>)
    }