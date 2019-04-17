/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from "react-apollo"; 
import {toast} from 'react-toastify';

import TabellaPiani from '../components/TabellaPiani'
import TabellaMessaggi from '../components/TabellaMessaggi'
import Button from '../components/IconButton'
import TextWithTooltip from '../components/TextWithTooltip'

import {GET_PIANI, DELETE_PIANO} from '../graphql'

const showError = (error) => {
    toast.error(error.message,  {autoClose: true})
}
 
const update = (cache, { data: {deletePiano : {success, codicePiano}}  = {}} = {}) => {
    if (success) {
        let { piani ={}} = cache.readQuery({ query: GET_PIANI}) || {}
        const edges = piani.edges.filter(({node}) => node.codice !== codicePiano)
        piani.edges = edges
        cache.writeQuery({
                        query: GET_PIANI,
                        data: { piani}
                    })
    }
}
const Piani = () => (
        <Query query={GET_PIANI}>
            {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
                if (error) {
                    toast.error(error.message,  {autoClose: true})
                }
                return ( <Mutation mutation={DELETE_PIANO} update={update} onError={showError}>
                    {(onDelete, m_props) => {
                        return (
                            <TabellaPiani title="piani in formazione" piani={edges} onDeletePiano={onDelete}></TabellaPiani>
                        )
                    }}
                </Mutation>)
            }}
        </Query>)
// const PianiArchiviati = () => (
//     <Query query={GET_PIANI}>
//         {({loading, data: {piani: {edges = []} = []} = {}, error}) => {
//             if (error) {
//                 toast.error(error.message,  {autoClose: true})
//             }
//             return (<TabellaPiani title="piani in corso" piani={edges}></TabellaPiani>)
//         }}
//     </Query>)

export default ({utente, ...props}) => {
    const {role: {type} = {}} = utente || {}
    return (
        <React.Fragment>
            <div>
                <h1>Portale della pianificazione</h1>
                <h3><TextWithTooltip dataTip="(L.R. 65/2014)" text="Software per la formazione e gestione dei piani"/></h3>
                <hr className="border-serapide border-bottom"></hr>
                <div className="py-4 d-flex flex-row">
                    <div className="d-flex flex-column ">
                        <h2>{`${utente.firstName || ""} ${utente.lastName || ""}`}</h2>
                    </div>
                    {type === "RUP" && <Button size='md' tag="a" href="./#/nuovo_piano" className="ml-auto my-auto text-uppercase" color="serapide" icon="note_add" label="Crea nuovo piano"></Button>}
                </div>
                
                <h5 className="py-5">I MIEI PIANI</h5>
                <Piani></Piani>
                <span className="legenda">LEGENDA NOTIFICHE</span>
                <div className="mr-4 pt-2 pb-5 d-flex flex-row justify-content-start legenda">
                    <i className="material-icons mr-1 urgente">notification_important</i><span>Il piano ha della azioni necessarie o in attesa</span>
                </div>
                <h6 className="py-5">MESSAGGI </h6>
                <TabellaMessaggi messaggi={utente.unreadMessages}></TabellaMessaggi>
                <a href="/users/messages/inbox/" className="mr-4 pt-4 pb-5 d-flex flex-row justify-content-end nav-link text-dark"><i className="material-icons mr-2">email</i><span>Tutti i messaggi</span></a>
                {/* <PianiArchiviati></PianiArchiviati>
                <a href="#/archivio" className="mr-4 pt-4 pb-5 d-flex flex-row justify-content-end nav-link text-dark"><i className="material-icons mr-2">view_list</i><span>Vai all'archivio piani</span></a> */}
            </div>
        </React.Fragment>)
    }