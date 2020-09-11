/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Route, Switch} from 'react-router-dom'
import { toast } from 'react-toastify'
import {Query} from "react-apollo"

import Anagrafica from './Anagrafica'
import Home from "./Home"
import Formazione from './Formazione'
import Avvio from './Avvio'
import Adozione from './Adozione'
import Approvazione from './Approvazione'
import Pubblicazione from './Pubblicazione'
import Injector from 'components/Injector'
import SideBar from 'components/SideBarMenu'
import StatoProgress from 'components/StatoProgress'
import Spinner from 'components/Spinner'

import {getEnteLabel, getPianoLabel, pollingInterval} from "utils"
import {GET_PIANI} from "schema"

import {toggleControllableState} from 'enhancers'
const enhancer = toggleControllableState("expanded", "toggleOpen", true)

const getActive = (url = "", pathname = "") => {
    return pathname.replace(url, "").split("/").filter(p => p !== "").shift()
}

class Piano extends React.PureComponent {

    componentDidMount() {
       
    }
    componentDidUpdate() {
       
    }
    componentWillUnmount() {
        
        this.props.stopPolling(pollingInterval)
    }

    render() {

        const {piano, url, path,location: {pathname} = {}, utente = {}, startPolling, stopPolling} = this.props;

        const activeLocation = getActive(url, pathname)
    return (<React.Fragment>
                <Injector el="serapide-sidebar">
                    <SideBar url={url} piano={piano} active={activeLocation} expanded={this.props.expanded} toggleOpen={this.props.toggleOpen} unreadMessages={utente.unreadThreadsCount}></SideBar>
                </Injector>
                    <div className={`${this.props.expanded ? "sidebar-open" : "sidebar-closed"} d-flex flex-column `}>
                        <div className="bg-white pt-5 pb-5 d-flex justify-content-between align-items-center piano-header">
                            <div className="flex-grow-1 pr-4">
                                <h4 className="text-uppercase h-pre mb-0">{getEnteLabel(piano.ente)}</h4>  
                                <div className="text-capitalize h-title">{`${getPianoLabel(piano.tipo)} ${piano.codice}`}</div>  
                                <div className="h-sub">{piano.descrizione}</div>
                                {piano?.esisteElaboratoCartograficoIngerito && <a className="text-blue pinter" href={`/geoportale/#/viewer/map?s_uid=${piano.codice}`}>Visualizza Mappa del Piano</a>}
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
                            <Route  path={`${path}/adozione`} >
                                <Adozione piano={piano}></Adozione>
                            </Route>
                            <Route  path={`${path}/approvazione`} >
                                <Approvazione piano={piano}></Approvazione>
                            </Route>
                            <Route  path={`${path}/pubblicazione`} >
                                <Pubblicazione piano={piano}></Pubblicazione>
                            </Route>
                            <Route  path={`${path}/home`} render={(props) => <Home startPolling={startPolling} stopPolling={stopPolling} utente={utente} azioni={piano.azioni} piano={piano} {...props}></Home>}/>
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
            </React.Fragment>
            )
    
    }
}

const PianoWithControlledSideBar = enhancer(Piano);

export default ({match: {url, path, params: {code} = {}} = {}, history, ...props}) => (
    <Query query={GET_PIANI} pollInterval={pollingInterval} variables={{codice: code}}>
        {({loading, data: {piani: {edges: [{node: piano} = {}] = []} = {}} = {}, error, networkStatus, ...queryProps}) => {
            if(loading && networkStatus !== 6){
                return <Spinner/>
            } else if(!piano) {
                toast.error(`Impossibile trovare il piano: ${code}`,  {autoClose: true, onClose: () => (history.back())})
                return <div></div>
            }
            return (<PianoWithControlledSideBar {...props} {...queryProps} piano={piano} url={url} path={path}/>)}
        }
    
    </Query>



)