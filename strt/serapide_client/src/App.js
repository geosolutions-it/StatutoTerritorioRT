/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {ApolloProvider} from 'react-apollo'
import { HashRouter as Router, Route, Switch } from 'react-router-dom';
import client from "./apolloclient"
import Dashboard from './pages/Dashboard'
import NuovoPiano from './pages/NuovoPiano'
import CreaAnagrafica from './pages/CreaAnagrafica'
import Piano from './pages/Piano'
import Injector from './components/Injector'
import ThemeInjector from './components/InjectSerapideTheme'
import NavBar from './components/NavigationBar'
import {globalAuth} from './autorizzazioni'

import  {ToastContainer} from 'react-toastify'
import {Query} from 'react-apollo'
import ReactTooltip from 'react-tooltip'

import '../node_modules/react-toastify/dist/ReactToastify.min.css'
import {GET_UTENTE} from "./graphql"

export default () => {
return (
    <ApolloProvider client={client}>
        <ToastContainer/>
        
        <Query query={GET_UTENTE} pollInterval={20000}>
        {({loading, data: {utenti: {edges = [{}]} = {}} = {}, error}) => {
            const {node: utente = {}} = edges[0]
            const {attore: themeClass, role: {type: ruolo} = {} } = utente
            
            if (loading) return (
                <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                    <div className="d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                    </div>
                </div>
                </div>)
                globalAuth._attore_attivo = themeClass
                globalAuth._ruolo = ruolo
            
            return(
                <React.Fragment>
                    <ThemeInjector themeClass={themeClass}/>
                    <Injector el="user-navbar-list">
                        <NavBar messaggi={utente.unreadMessages} alertsCount={utente.alertsCount}  roleType={ruolo}/>
                    </Injector>
                    <ReactTooltip></ReactTooltip>
                    <div className="serapide-content pt-5 pb-5 pX-lg-1 pX-xl-2 px-4 serapide-top-offset position-relative overflow-auto">
                            <Router>
                                <Switch>
                                    <Route  path="/piano/:code" render={(props) => <Piano utente={utente} {...props}/>} />
                                    <Route  path="/crea_anagrafica/:code" component={CreaAnagrafica}/>
                                    <Route  path="/nuovo_piano/" >
                                    {utente && utente.role && utente.role.type === "RUP" && <NuovoPiano utente={utente}></NuovoPiano>}
                                    </Route>             
                                    <Route  path="/" render={(props) => <Dashboard utente={utente} {...props}/>}/>
                                </Switch>
                            </Router>
                    </div>
                </React.Fragment>)
        }}
        </Query>
      </ApolloProvider>
    )
}
