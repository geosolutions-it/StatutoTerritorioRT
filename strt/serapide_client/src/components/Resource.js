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
import {formatDate, isEmpty} from 'utils'
import TextWithTooltip from './TextWithTooltip'

const getFileSize = (dim) => dim ? `${Math.round(parseFloat(dim)/100)/10} MB` : null


const ResourceTitle = ({resource: {downloadUrl, label = "", tooltip = "", nome} = {}, useLabel, fontSize} = {}) => {
    
    const lab = useLabel && label ?  label : nome
    const tip = (<TextWithTooltip dataTip={tooltip} className={fontSize} dataTipDisable={!useLabel} text={lab}/>)
    return downloadUrl ?(
            <a target="_blank" rel="noopener noreferrer" className={`text-dark ${fontSize}`} href={downloadUrl} download={nome}>
                {useLabel && tooltip ? tip : lab}
            </a>) : (
        <span className={fontSize} >{useLabel && tooltip ? tip : lab}</span>)
}
const ResourceTools = ({downloadUrl, downloadIcon, nome, isLocked, iconClasses, confirm} = {}) => {
    return <React.Fragment>
                {downloadUrl ? (
                    <a className="text-dark d-flex" target="_blank" rel="noopener noreferrer" href={downloadUrl} download={nome}>
                {downloadIcon} </a>) : downloadIcon}
                {isLocked ? (<i className={iconClasses}>lock</i>) : (<i className={`${iconClasses} pointer`} onClick={confirm} >cancel</i>)}
            </React.Fragment>
}

export default ({
    resource = {},
    className ="resource",
    icon = "picture_as_pdf",
    iconSize,
    fontSize,
    codice,
    isLoading,
    isLocked = true,
    useLabel = false,
    fileSize = true,
    vertical = false,
    onDeleteResource = () => {console.warn("Delete mutation non passata")}} = {}) => {
    const  { nome, uuid, lastUpdate, dimensione, downloadUrl} =  resource ?? {};
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
    const iconClasses = `material-icons text-serapide ${iconSize}`;
    const downloadIcon = (<i className={ ` ${iconClasses} pointer `}>{isLocked ? "cloud_download" : "check_circle"}</i>);
    if (isEmpty(resource)) {
        return <div className={`${className} row align-items-center`}></div>
    }
    return  !vertical ? (
        <div className={`${className} row align-items-center`}>
            <div className="col-6 d-flex">
                <i className={`${iconClasses} align-self-center `}>{icon}</i>
                <div className={`pl-1 d-flex flex-column justify-content-between ${fontSize}`}>
                <ResourceTitle fontSize={fontSize} resource={resource} useLabel={useLabel}/>
                {fileSize && (<span style={{fontSize: "0.8em"}}>{getFileSize(dimensione)}</span>)}
            </div></div>
            <div className={`col-3 ${fontSize}`}>{lastUpdate && formatDate(lastUpdate, "dd/MM/yyyy")}</div>
            <div className="col-3 d-flex justify-content-end">
                {isLoading ? (<div className="spinner-grow text-serapide" role="status">
                    <span className="sr-only">Loading...</span>                
                </div>) : (<ResourceTools
                                downloadUrl={downloadUrl} 
                                downloadIcon={downloadIcon}
                                nome={nome}
                                isLocked={isLocked}
                                iconClasses={iconClasses}
                                confirm={confirm}/>)}
            </div>
        </div>) : (
            <div className={`${className} row align-items-center`}>
                <div className="col-10 d-flex">
                    <i className={`${iconClasses} align-self-center `}>{icon}</i>
                    <div className={`pl-1 d-flex flex-column justify-content-between ${fontSize}`}>
                        <ResourceTitle fontSize={fontSize} resource={resource} useLabel={useLabel}/>
                        { useLabel && resource.label && (<span>{resource.nome}</span>)}
                        <span className="d-flex align-items-center">
                            {lastUpdate && (<span>{formatDate(lastUpdate, "dd/MM/yyyy")}</span>)}
                            {fileSize && (<span className="offset-4 text-nowrap" style={{fontSize: "0.8em"}}>{getFileSize(dimensione)}</span>)}
                        </span>
                    </div>
                </div>
                <div className="col-2 d-flex justify-content-end">
                    {isLoading ? (<div className="spinner-grow text-serapide" role="status">
                            <span className="sr-only">Loading...</span>                
                        </div>) : (<ResourceTools
                                    downloadUrl={downloadUrl} 
                                    downloadIcon={downloadIcon}
                                    nome={nome}
                                    isLocked={isLocked}
                                    iconClasses={iconClasses}
                                    confirm={confirm}/>)
                    }          
                </div>
            </div>)
}
