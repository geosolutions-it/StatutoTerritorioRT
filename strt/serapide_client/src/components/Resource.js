/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import { toast } from 'react-toastify'
import Confirm from './ConfirmToast'

const getFileSize = (dim) => dim ? `${Math.round(parseFloat(dim)/100)/10} MB` : null
export default ({resource: { nome, uuid, tipo, dimensione, downloadUrl}, className ="resource", icon = "picture_as_pdf", codice, isLoading , isLocked = true, onDeleteResource = () => {console.warn("Delete mutation non passata")}} = {}) => {
    let toastId
    const deleteResource = () => onDeleteResource({ variables: { id: uuid, codice}})
    const confirm = () => {
        if(!toast.isActive(toastId)) {
        toastId = toast.warn(<Confirm confirm={deleteResource} id={uuid} />, {
            autoClose: true,
            draggable: true,
            // hook will be called whent the component unmount
            onClose: ( ) => {toastId = null}
          });
        }
    }
    return  (
        <div className={`${className} d-flex justify-content-between align-items-center`}>
            <div className="d-flex">
                <i className="material-icons text-serapide">{icon}</i>
            <div className="pl-1 d-flex flex-column justify-content-between">
                {downloadUrl ? (<a className="text-dark"href={downloadUrl} download={nome}>{nome}</a>) : (
                <span>{nome}</span>)}
                <span style={{fontSize: "0.8rem"}}>{getFileSize(dimensione)}</span>
            </div></div>
            <div className="d-flex justify-content-center align-items-center">
                {isLoading && (<div className="spinner-grow text-serapide" role="status">
                    <span className="sr-only">Loading...</span>                
                </div>)}
                {downloadUrl ? (
                <a className="text-dark d-flex" href={downloadUrl} download={nome}>
                    <i className="material-icons text-serapide pointer">{isLocked ? "cloud_download" : "check_circle"}</i></a>) :
                (<i className="material-icons text-serapide pointer">{isLocked ? "cloud_download" : "check_circle"}</i>)}
                
                {isLocked ? (
                    <i className="material-icons text-serapide">lock</i>
                ) : (
                    <i className="material-icons text-danger" onClick={confirm} style={{cursor: 'pointer'}}>cancel</i>
                ) }
            </div>
        </div>)
}
