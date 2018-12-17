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
import Home from './pages/Home'
import NuovoPiano from './pages/NuovoPiano'
import Injector from './components/Injector'
import NavBar from './components/NavigationBar'
import {messaggi} from './resources'
export default () => {
    return (
        <ApolloProvider client={client}>
         <Injector el="user-navbar-list">
           <NavBar messaggi={messaggi}/>
         </Injector>
          <Router>
            <Switch>
              <Route  path="/nuovo_piano/" component={NuovoPiano}/>             
              <Route  path="/" component={Home}/>
            </Switch>
          </Router>
        </ApolloProvider>
    )
}
