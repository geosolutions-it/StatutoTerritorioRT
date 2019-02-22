/*
 * Copyright 2018, GeoSolutions Sas.
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
import {getThemeClass} from "./utils"

import  {ToastContainer} from 'react-toastify'
import {Query} from 'react-apollo'
import '../node_modules/react-toastify/dist/ReactToastify.min.css'
import {GET_UTENTE} from "./queries"

export default () => {
return (
    <ApolloProvider client={client}>
        <ToastContainer/>
        <Query query={GET_UTENTE} pollInterval={20000}>
        {({loading, data: {utenti: {edges= []} = {}} = {}, error}) => {
            const {node: utente = {}} = edges[0] || {}
            const {contactType, role: {organization : {type: {code} = {}} = {}} = {} } = utente || {}
            const themeClass = getThemeClass(contactType, code)
            if (loading) return (
                <div className="serapide-content pt-5 pb-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                    <div className="d-flex justify-content-center">
                        <div className="spinner-grow " role="status">
                            <span className="sr-only">Loading...</span>
                    </div>
                </div>
                </div>)
            return(
                <React.Fragment>
                 <ThemeInjector themeClass={themeClass}/>
                  <Injector el="user-navbar-list">
                      <NavBar messaggi={utente.unreadMessages} alertsCount={utente.alertsCount}/>
                  </Injector>
                  <Router>
                      <Switch>
                          <Route  path="/piano/:code" render={(props) => <Piano utente={utente} {...props}/>} />
                          <Route  path="/crea_anagrafica/:code" component={CreaAnagrafica}/>
                          <Route  path="/nuovo_piano/" component={NuovoPiano}/>             
                          <Route  path="/" render={(props) => <Dashboard utente={utente} {...props}/>}/>
                      </Switch>
                  </Router>
                </React.Fragment>)
        }}
        </Query>
      </ApolloProvider>
    )
}
