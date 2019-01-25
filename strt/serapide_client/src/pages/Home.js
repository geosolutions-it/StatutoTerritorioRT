/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


import TabellaPiani from '../components/TabellaPiani'
import TabellaMessaggi from '../components/TabellaMessaggi'
import Button from '../components/IconButton'
import {defaultProps} from 'recompose'

import {Query} from "react-apollo"; 
import {toast} from 'react-toastify';

import {user, messaggi}  from '../resources'
import {GET_PIANI} from '../queries'


const Piani = () => (
        <Query query={GET_PIANI}>
            {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
                if (error) {
                    toast.error(error.message,  {autoClose: true})
                }
                return (<TabellaPiani title="piani in corso" piani={edges}></TabellaPiani>)
            }}
        </Query>)
const PianiArchiviati = () => (
    <Query query={GET_PIANI}>
        {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
            if (error) {
                toast.error(error.message,  {autoClose: true})
            }
            return (<TabellaPiani title="piani in corso" piani={edges}></TabellaPiani>)
        }}
    </Query>)

export default defaultProps({user, messaggi})((props) => {
    return (
        <React.Fragment>
            <div className="serapide-content pt-5 pX-md px-1 serapide-top-offset position-relative overflow-x-scroll">
                <h1>Portale del territorio</h1>
                <h2>Strumenti per la formazione e gestione dei piani</h2>
                <hr className="border-warning border-bottom"></hr>
                <div className="py-4 d-flex flex-row">
                    <div className="d-flex flex-column ">
                        <h2>{props.user.nome}</h2>
                        <p>{props.user.organizzazione}</p>
                    </div>
                    <Button size='md' tag="a" href="./#/nuovo_piano" className="ml-auto my-auto text-uppercase" color="warning" icon="note_add" label="Crea nuovo piano"></Button>
                    <div className="px-sm-4"></div>
                    <Button size='md' tag="a" href="./#/archivio" className="my-auto text-uppercase" color="warning" icon="view_list" label="archivio piani"></Button>
                </div>
                
                <h5 className="py-5">I MIEI PIANI</h5>
                <Piani></Piani>
                <span className="legenda">LEGENDA NOTIFICHE</span>
                <div className="mr-4 pt-2 pb-5 d-flex flex-row justify-content-start legenda">
                    <i className="material-icons mr-1 urgente">notification_important</i><span >Notifiche urgenti per le quali è richiesta un'azione</span>
                    <i className="material-icons mr-1 importante">notification_important</i><span >Notifiche importanti per le quali è richiesta un'azione</span>
                    <i className="material-icons mr-1 prossimamente">notification_important</i><span >Notifiche urgenti per le quali è richiesta un'azione</span>
                </div>
                <h6 className="py-5">MESSAGGI </h6>
                <TabellaMessaggi messaggi={props.messaggi}></TabellaMessaggi>
                <a href="#/messaggi" className="mr-4 pt-4 pb-5 d-flex flex-row justify-content-end nav-link text-dark"><i className="material-icons mr-2">email</i><span>Tutti i messaggi</span></a>
                <PianiArchiviati></PianiArchiviati>
                <a href="#/archivio" className="mr-4 pt-4 pb-5 d-flex flex-row justify-content-end nav-link text-dark"><i className="material-icons mr-2">view_list</i><span>Vai all'archivio piani</span></a>
            </div>
        </React.Fragment>)
    })