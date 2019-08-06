/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { Table } from 'reactstrap'
import StatoProgress from './StatoProgress'
import {formatDate} from 'utils'
import { toast } from 'react-toastify'
import Confirm from './ConfirmToast'


const {Fragment} = React;
const goToAnagrafica = (codice, {nome} = {}) => {
    if(nome === "DRAFT"){
         window.location.href=`#/crea_anagrafica/${codice}`
        }else {
            window.location.href=`#/piano/${codice}/anagrafica`
        }
}
const goToPiano = (codice) => {
        window.location.href=`#/piano/${codice}/home`
}
const isDelete = ({nome = "Unknown"}) => (nome === 'DRAFT' || nome === "Unknown")

const reverseOrderByUpdate = ({node: {lastUpdate: a}}, {node: {lastUpdate: b}}) => {
    if(a === b) {
        return 0
    }
    if(a > b) {
        return -1
    }
    return 1    
}

export default ({title, piani = [], onDeletePiano = () => console.warn("Aggiungere query per eliminazione piano")}) => {
    const deleteResource = (codice) => onDeletePiano({ variables: {codice}})
    const confirm = (codice) => {
        if(!toast.isActive(codice)) {
            toast.warn(<Confirm label="Eliminare definitavmente il piano?" confirm={deleteResource} id={codice} />, {
                autoClose: true,
                draggable: true,
                id: codice,
                // hook will be called whent the component unmount
                onClose: ( ) => {}
            });
        }
    }    
    
    return (
    <Fragment>
        <h6 className="pb-3 text-uppercase">{title}</h6>
        <Table className="pb-4" size="sm" striped>
            <thead>
                <tr>
                    <th >Notifiche</th>
                    <th >Nome Piano</th>
                    <th >Tipo</th>
                    <th >Ultima Modifica</th>
                    <th >Codice Unico</th>
                    <th >Anagrafica</th>
                    <th >Stato</th>
                    <th >RUP</th>
                    <th >Riprendi procedimento</th>
                </tr>
            </thead>
            <tbody>
                {piani.sort(reverseOrderByUpdate).map(({node: {alertsCount = 0, descrizione, tipo, lastUpdate, codice, fase = {}, user= {}}} = {}) => (
                    <tr key={codice}>
                        <td className="text-center">{alertsCount > 0 && (<i className="material-icons text-danger">notification_important</i>)}</td>
                        <td style={{maxWidth: 350}}>{descrizione}</td>
                        <td className="text-center text-capitalize">{tipo}</td>
                        <td className="text-center">{formatDate(lastUpdate)}</td>
                        <td className="text-center">{codice}</td>
                        <td className="text-center" style={{cursor: "pointer"}} onClick={() => goToAnagrafica(codice, fase)}><i className="material-icons text-serapide">assignment</i></td>
                        <td>
                            <StatoProgress stato={fase}></StatoProgress>
                        </td>
                        <td className="text-justify text-center">{user && `${user.firstName || ''} ${user.lastName || ''}`}</td>
                        <td className="text-center" style={{cursor: "pointer"}} onClick={() => (isDelete(fase) ? confirm(codice) :  goToPiano(codice))}><i className="material-icons text-serapide">{isDelete(fase) ? "delete" : "play_circle_filled"}</i></td>
                    </tr>))}
                </tbody>
            </Table>

    </Fragment>
)}
    

