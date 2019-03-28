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
import {formatDate} from '../utils'
import TextWithTooltip from './TextWithTooltip'
const getFileSize = (dim) => dim ? `${Math.round(parseFloat(dim)/100)/10} MB` : null


const ResourceTitle = ({resource: {downloadUrl, label, tooltip, nome} = {}, useLabel} = {}) => {
    const lab = useLabel ?  label : nome
    const tip = (<TextWithTooltip dataTip={tooltip} dataTipDisable={!useLabel} text={label}/>)
    return downloadUrl ?(
            <a target="_blank" rel="noopener noreferrer" className="text-dark" href={downloadUrl} download={nome}>
                {useLabel ? tip : lab}
            </a>) : (
        <span >{useLabel ? tip : lab}</span>)
}

export default ({
    resource = {},
    className ="resource",
    icon = "picture_as_pdf",
    codice,
    isLoading,
    isLocked = true,
    useLabel = false,
    fileSize = true,
    onDeleteResource = () => {console.warn("Delete mutation non passata")}} = {}) => {
    const  { nome, uuid, lastUpdate, dimensione, downloadUrl} = resource;
    let toastId
    const deleteResource = () => onDeleteResource({ variables: { id: uuid, codice}})
    const confirm = () => {
        if(!toast.isActive(toastId)) {
        toastId = toast.warn(<Confirm confirm={deleteResource} id={uuid} />, {
            autoClose: true,
            draggable: true,
            // hook will be called  whent the component unmount
            onClose: ( ) => {toastId = null}
          });
        }
    }
    return  (
        <div className={`${className} row align-items-center`}>
            
            <div className="col-6 d-flex">
                <i className="material-icons text-serapide align-self-center">{icon}</i>
                <div className="pl-1 d-flex flex-column justify-content-between">
                <ResourceTitle resource={resource} useLabel={useLabel}/>
                {fileSize && (<span style={{fontSize: "0.8rem"}}>{getFileSize(dimensione)}</span>)}
            </div></div>
            <div className="col-3">{lastUpdate && formatDate(lastUpdate, "dd MMMM yyyy")}</div>
            <div className="col-3 d-flex justify-content-end">
                {isLoading && (<div className="spinner-grow text-serapide" role="status">
                    <span className="sr-only">Loading...</span>                
                </div>)}
                {downloadUrl ? (
                <a className="text-dark d-flex" target="_blank" rel="noopener noreferrer" href={downloadUrl} download={nome}>
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
