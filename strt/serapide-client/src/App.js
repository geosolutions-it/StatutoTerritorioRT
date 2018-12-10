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

export default () => {
    return (
        <ApolloProvider client={client}>
          <Router>
            <Switch>
              <Route  path="/" component={Home}/>
              <Route path="/about" component={()=> (<div>Puppa</div>)}/>
            </Switch>
          </Router>
        </ApolloProvider>
    )
}
