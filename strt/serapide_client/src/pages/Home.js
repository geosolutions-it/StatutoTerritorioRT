/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Azioni from '../components/TabellaAzioni'
import AvvioConsultazioniSCA from "./actions/AvvioConsultazioneSCA"
import PareriSCA from "./actions/PareriSCA"
import {Switch, Route} from 'react-router-dom'
import classNames from 'classnames'
const getAction = (url = "", pathname = "") => {
    return pathname.replace(url, "").split("/").filter(p => p !== "").shift()
}

export default ({match: {url, path, params: {code} = {}} = {},location: {pathname} = {}, history, utente = {}, azioni = []}) => {
    const action = getAction(url, pathname)
    const goToAction = (action = "") => {

        window.location.href = `#${url}/${action.toLowerCase().replace(" ","_")}`
    } 
    return (
    <div className="d-flex pb-4 pt-5">
        <div className={classNames("d-flex flex-column flex-1")}>
            <div className="d-flex border-serapide border-top border-bottom py-4 justify-content-around">
                <span>LEGGENDA</span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_add</i><span>E’ richiesta un’azione</span></span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_on</i><span>In attesa di risposta da altri attori</span></span>
                <span className="d-flex"><i className="material-icons text-serapide mr-2">alarm_off</i><span>Nessuna azione richiesta</span></span>
            </div>
            <div className="py-4">
                <Azioni azioni={azioni} onExecute={goToAction}/>
            </div>
        </div >
        <div className={classNames("d-flex flex-column ", {"ml-2  pl-3 flex-2 border-left": action})}>
            {action && <div  className="mb-3 close  align-self-end" onClick={() => history.push(url)}>x</div>}
            <Switch>
                <Route path={`${path}/avvio_consultazioni_sca`} >
                    <AvvioConsultazioniSCA onClose={history.goBack} codicePiano={code}></AvvioConsultazioniSCA>
                </Route>
                <Route path={`${path}/pareri_sca`} >
                    <PareriSCA></PareriSCA>
                </Route>
                { action && (
                <Route path={path}>
                    <div className="p-6"> Azione non ancora implementata</div>
                </Route>)}
            </Switch>
        </div>
    </div>
)}