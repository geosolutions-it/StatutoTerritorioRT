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
import NavBar from './components/NavigationBar'

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
            return(
                <React.Fragment>
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
