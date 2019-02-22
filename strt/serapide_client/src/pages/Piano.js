/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import { toast } from 'react-toastify'
import { Route, Switch} from 'react-router-dom';
import {Query} from "react-apollo"
import Anagrafica from './Anagrafica'
import Formazione from './Formazione'
import {getEnteLabel, getPianoLabel} from "../utils"
import {GET_PIANI} from "../queries"
import Injector from '../components/Injector'
import SideBar from '../components/SideBarMenu'
import StatoProgress from '../components/StatoProgress'
import Home from "./Home"


const getActive = (url = "", pathname = "") => {
    return pathname.replace(url, "")
}
export default ({match: {url, path, params: {code} = {}} = {},location: {pathname} = {}, utente = {}, ...props}) => {
    const activeLocation = getActive(url, pathname)
    return (<Query query={GET_PIANI} variables={{codice: code}}>

        {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
            if(loading){
                return (
                    <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                    </div>)
            } else if(edges.length === 0) {
                toast.error(`Impossibile trovare il piano: ${code}`,  {autoClose: true})
                return <div></div>
            }
            const {node: piano = {}} = edges[0] || {}
            const {edges: azioni} = piano.azioni || {}
            return(
            <React.Fragment>
                <Injector el="serapide-sidebar">
                    <SideBar url={url} piano={piano} active={activeLocation} unreadMessages={utente.unreadThreadsCount}></SideBar>
                </Injector>
                <div className="serapide-content pt-5 pb-5 pX-lg px-4 serapide-top-offset position-relative">
                    <div className="d-flex flex-column ">
                        <div className="d-flex justify-content-between align-items-center ">
                            <div className="pr-3">
                                <h4 className="text-uppercase">{getEnteLabel(piano.ente)}</h4>  
                                <h2 className="mb-0 text-capitalize">{`${getPianoLabel(piano.tipo)} ${code}`}</h2>  
                                <div className="pr-4">{piano.descrizione}</div>  
                            </div>
                            <StatoProgress className="stato-progress-xxl" stato={piano.fase} legend></StatoProgress>
                        </div>
                        <Switch>
                            <Route  path={`${path}/anagrafica`} component={Anagrafica}/>
                            <Route  path={`${path}/formazione`} component={Formazione}/>
                            <Route  path={`${path}`}>
                                <Home azioni={azioni}></Home>
                            </Route>
                        </Switch>
                        
                            
                    </div>
                   
                </div>
            </React.Fragment>
            )}
        }
    </Query>)
    }