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
import Avvio from './Avvio'
import {getEnteLabel, getPianoLabel} from "utils"
import {GET_PIANI} from "schema"
import Injector from 'components/Injector'
import SideBar from 'components/SideBarMenu'
import StatoProgress from 'components/StatoProgress'
import Home from "./Home"


const getActive = (url = "", pathname = "") => {
    return pathname.replace(url, "").split("/").filter(p => p !== "").shift()
}
export default ({match: {url, path, params: {code} = {}} = {},location: {pathname} = {}, utente = {}, ...props}) => {
    const activeLocation = getActive(url, pathname)
    return (<Query query={GET_PIANI} pollInterval={10000} variables={{codice: code}}>

        {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
            if(loading){
                return (
                        <div className="d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>
                    )
            } else if(edges.length === 0) {
                toast.error(`Impossibile trovare il piano: ${code}`,  {autoClose: true, onClose: () => (window.location.assign(window.location.href.replace(pathname, "")))})
                return <div></div>
            }
            const {node: piano = {}} = edges[0] || {}
            const {edges: azioni} = piano.azioni || {}
            return(
            <React.Fragment>
                <Injector el="serapide-sidebar">
                    <SideBar url={url} piano={piano} active={activeLocation} unreadMessages={utente.unreadThreadsCount}></SideBar>
                </Injector>
                <div>
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
                            <Route  path={`${path}/formazione`} >
                                <Formazione utente={utente} piano={piano}></Formazione>
                            </Route>
                            <Route  path={`${path}/avvio`} >
                                <Avvio piano={piano}></Avvio>
                            </Route>
                            <Route  path={`${path}/home`} render={(props) => <Home utente={utente} azioni={azioni} piano={piano} {...props}></Home>}/>
                            <Route path={path}>
                                <div className="p-6"><h1> Works in progress </h1> 
                                    <div className="d-flex justify-content-center">
                                        <div className="spinner-grow " role="status">
                                            <span className="sr-only">Loading...</span>
                                        </div>
                                    </div>
                                </div>
                            </Route>       
                        </Switch>
                        
                            
                    </div>
                   
                </div>
            </React.Fragment>
            )}
        }
    </Query>)
    }