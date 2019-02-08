/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import classeNames from 'classnames'
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'

const Switch = ({isLocked, label, value, toggleSwitch = (k) => {console.log(k)}, className, children, checked }) => {
    const toggle = () => { 
        if(!isLocked) {
            toggleSwitch(!checked, value)
        }
    }
    return (
        <React.Fragment>
            <div key={value}  className={classeNames('strt-switch','d-flex', 'direction-column', className)}>
                <span className="pr-3">{label}</span>
                <div  className="switch-label custom-control custom-switch">
                    <label  onClick={toggle} style={{cursor: isLocked ? 'not-allowed' : 'pointer'}} className={classeNames('custom-control-label', {checked})}></label>
                </div>  
            </div>
            {children(checked)}
        </React.Fragment>)
    }
export default Switch

const showError = (error, onError) => {
    toast.error(error.message,  {autoClose: true})
}
const _getInput = () => ({variables: {input: {}}})

export const EnhancedSwitch  = ({isLocked, mutation, update, getInput = _getInput, label, value, className, children, checked,  ...mutationProps}) => {
    return (
    <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
        {(onChange, m_props) => {
            const toggleSwitch = (checked, val) => {
                if (checked) {
                    onChange(getInput(val))
                }
            }
            return (
                <Switch isLocked={isLocked} toggleSwitch={toggleSwitch} label={label} value={value} className={className} children={children} checked={checked}/>
            )
        }}
    </Mutation>)
}