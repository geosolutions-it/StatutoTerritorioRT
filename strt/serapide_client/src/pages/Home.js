/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Switch, Route, Redirect} from 'react-router-dom'
import Azioni from 'components/TabellaAzioni'
import FaseSwitch from 'components/FaseSwitch'
import actions from './actions'

import classNames from 'classnames'
import { getAction, pollingInterval, showAdozione, showApprovazione, showPubblicazione} from 'utils'
import {stopStartPolling} from 'enhancers'

import {camelCase} from 'lodash'
// import {map, snakeCase} from 'lodash'


const polling = stopStartPolling(pollingInterval)
const components = Object.keys(actions).reduce((c,k) => ({...c, [k]: polling(actions[k])}), {})

const getCurrentAction = (url = "", pathname = "") => {
    return pathname.replace(url, "").split("/").filter(p => p !== "").shift()
}

const NotAvailable = () => (<div className="p-6">Azione non implementata</div>)

export default class Home extends React.PureComponent{

render () {
    
    const {match: {url, path} = {},
           location: {pathname} = {}, history, utente = {attore: ""}, piano = {},
           azioni = [],
           startPolling, stopPolling} = this.props;
    console.log("Home", azioni)
    const action = getCurrentAction(url, pathname)
    const scadenza = azioni.filter(({tipologia = ""} = {}) => tipologia.toLowerCase().replace(" ","_") === action).map(({data, }) => data).shift()
    const goToAction = (action = "", uuid) => {
        history.push(`${url}/${action.toLowerCase().replace(" ","_")}/${uuid}`)
    }
    const {fase: nomeFase} = piano
    const goBack = () => {
        history.push(url)
    }
    return (
    <div className="d-flex flex-column pb-4">
        <div className="legenda-azioni bg-white pb-4 border-piano border-bottom">
            <div className="d-flex border-serapide border-top border-bottom py-4 justify-content-around legenda-azioni">
                <span className="my-auto">LEGENDA</span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_add</i><span className="size-13 align-self-center">E’ richiesta un’azione</span></span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_on</i><span className="size-13 align-self-center">In attesa di risposta da altri attori</span></span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_off</i><span className="size-13 align-self-center">Nessuna azione richiesta</span></span>
            </div>
        </div>
        <div className="d-flex home-container ">
            <div className={classNames("lista-azioni bg-white border  d-flex flex-column flex-1", {"flex-fill": !action})}>
                
                {showPubblicazione(nomeFase) && (<FaseSwitch initValue={nomeFase==="APPROVAZIONE"} fase="pubblicazione" goToSection={() => history.push(url.replace("home","pubblicazione"))}>
                    <div className="py-4">
                        <Azioni azioni={azioni} filtroFase="approvazione" onExecute={goToAction}/>
                    </div>
                </FaseSwitch>)}
                {showApprovazione(nomeFase) && (<FaseSwitch initValue={nomeFase==="ADOZIONE"} fase="approvazione" goToSection={() => history.push(url.replace("home","approvazione"))}>
                    <div className="py-4">
                        <Azioni azioni={azioni} filtroFase="adozione" onExecute={goToAction}/>
                    </div>
                </FaseSwitch>)}
                {showAdozione(nomeFase) && (<FaseSwitch initValue={nomeFase==="AVVIO"} fase="adozione" goToSection={() => history.push(url.replace("home","adozione"))}>
                    <div className="py-4">
                        <Azioni azioni={azioni} filtroFase="avvio" onExecute={goToAction}/>
                    </div>
                </FaseSwitch>)}
                <FaseSwitch initValue={nomeFase==="ANAGRAFICA"} fase="avvio" goToSection={() => history.push(url.replace("home","avvio"))}>
                    <div className="py-4">
                        <Azioni azioni={azioni} onExecute={goToAction}/>
                    </div>
                </FaseSwitch>
            </div >
            <div className={classNames("d-flex flex-column", {"action-container flex-1 border  border-piano overflow-auto bg-white": action})}>
                {action && <div  className="mb-3 close  align-self-end" onClick={() => history.push(url)}>x</div>}
                <Switch>
                    { azioni.map(({uuid, tipologia = "", label = "", attore = "", eseguibile= false} = {}) => {
                        const tipo = tipologia.toLowerCase()
                        const El = components[camelCase(tipo)]
                        return El && (
                                <Route exact key={tipo} path={`${path}/${tipo}/${uuid}`} >
                                    {eseguibile ? (<El startPolling={startPolling} stopPolling={stopPolling} piano={piano} back={goBack} utente={utente} scadenza={scadenza}/>) : (<Redirect to={url} />)}
                                </Route>)
                    })}
                    {/* {map(components, (El, key) => {
                        const tipo = snakeCase(key)
                        
                        return El && (
                                <Route key={key} path={`${path}/${tipo}`} >
                                    <El piano={piano} back={goBack} utente={utente} scadenza={scadenza}/>
                                </Route>)
                    })} */}
                    { action && (
                    <Route path={path}>
                        <NotAvailable/>
                    </Route>)}
                </Switch>
            </div>
        </div>
    </div>
)}

}