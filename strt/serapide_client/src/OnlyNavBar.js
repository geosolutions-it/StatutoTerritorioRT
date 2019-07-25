/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {ApolloProvider} from 'react-apollo'

import client from "./apolloclient"
import Injector from './components/Injector'
import ThemeInjector from './components/InjectSerapideTheme'
import NavBar from './components/NavigationBar'
import {globalAuth} from './autorizzazioni'


import {Query} from 'react-apollo'



import {GET_UTENTE} from "./graphql"
import {pollingInterval} from 'utils'
export default () => {
return (
    <ApolloProvider client={client}>

        
        <Query query={GET_UTENTE} pollInterval={pollingInterval}>
        {({loading, data: {utenti: {edges = [{}]} = {}} = {}, error}) => {
            const {node: utente = {}} = edges[0]
            const {attore: themeClass, role: {type: ruolo} = {} } = utente
            
            if (loading) return null
            globalAuth._attore_attivo = themeClass
            globalAuth._ruolo = ruolo
            
            return(
                <React.Fragment>
                    <ThemeInjector themeClass={themeClass}/>
                    <Injector el="user-navbar-list">
                        <NavBar messaggi={utente.unreadMessages} alertsCount={utente.alertsCount} attore={utente.attore} roleType={ruolo}/>
                    </Injector>
                </React.Fragment>)
        }}
        </Query>
      </ApolloProvider>
    )
}
