/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import MenuItem from './MenuItem'
import ReactTooltip from 'react-tooltip'
// import {Badge} from 'reactstrap'
import {showAdozione, showApprovazione, showPubblicazione} from 'utils'

export default ({piano = {}, expanded, url, active, toggleOpen, unreadMessages = 0}) => (
    <React.Fragment>
        <ReactTooltip id="sidebar-tooltip"/>
        {expanded ? (
            <div className="sidebar-header">
            <span className="close text-serapide" onClick={toggleOpen}><i className="material-icons">close</i></span>
                <div className="d-flex flex-column pt-2">
                    <div className="title-portale">PORTALE DEL TERRITORIO</div>
                    <div className="piano-title text-capitalize">{`${piano.codice}`}</div>
                </div>
            </div>) : (
            <div className="sidebar-header collapsed" onClick={toggleOpen}><i className="material-icons pointer">reorder</i></div>)}
        
            <ul className="list-group">
                <MenuItem href={active !== "home" && `${url}/home`} active={active === "home"} title="HOME PIANO" icon="home" expanded={expanded}/>
                <MenuItem href={`${url}/anagrafica`} active={active === "anagrafica"} title="ANAGRAFICA" icon="assignment" expanded={expanded}/>
                <MenuItem  className="border-bottom-3" href={`${url}/formazione`} active={active === "formazione"} title="FORMAZIONE PIANO" subtitle="Accesso agli strumenti" icon="build" expanded={expanded}/>
                
                <MenuItem href={`${url}/avvio`} active={active === "avvio"} title="AVVIO" subtitle="Avvio del Procedimento" icon="dashboard" expanded={expanded}/>
                
                <MenuItem locked={!showAdozione(piano.fase.nome)} href={`${url}/adozione`} active={active === "adozione"} title="ADOZIONE" icon="library_add" expanded={expanded}/>
                <MenuItem locked={!showApprovazione(piano.fase.nome)} href={`${url}/approvazione`} active={active === "approvazione"} title="APPROVAZIONE" icon="offline_pin" expanded={expanded}/>
                <MenuItem locked={!showPubblicazione(piano.fase.nome)} href={`${url}/pubblicazione`} active={active === "pubblicazione"} title="PUBBLICAZIONE" icon="turned_in" expanded={expanded}/>
                {/* <MenuItem href="/users/messages/inbox/" active={active === "/messaggi"} title="MESSAGGI" icon="email" expanded={expanded}>
                    <Badge color="light">{unreadMessages}</Badge>
                </MenuItem> */}
                {/* <MenuItem href={`#${url}/avvisi`} active={active === "/avvisi"} title="ALERT" icon="notification_important" iconColor="text-danger" expanded={expanded}>
                    <Badge color="light">{piano.alertsCount || "0"}</Badge>
                </MenuItem> */}
                
            </ul>
    </React.Fragment>
)