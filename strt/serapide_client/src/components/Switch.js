/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import classeNames from 'classnames'
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'
import {isFunction} from 'lodash'
import {toggleControllableState} from 'enhancers'

const enhancer = toggleControllableState('checked', 'toggleSwitch', false)
const Switch = ({isLocked, label, value, toggleSwitch = (k) => {console.log(k)}, className, children, checked, labelClassName = "col-xl-4 col-lg-6 col-md-6 col-10"}) => {
    const toggle = () => { 
        if(!isLocked) {
            toggleSwitch(!checked, value)
        }
    }
    return !isLocked || checked ? (
        <React.Fragment>
            <div key={value}  className={classeNames('strt-switch','row', className, {"mt-3": isLocked})}>
                <span className={labelClassName}>{label}</span>
                {!isLocked && (
                <div  className="switch-label custom-control custom-switch col-1">
                    <label  onClick={toggle} style={{cursor: isLocked ? 'not-allowed' : 'pointer'}} className={classeNames('custom-control-label', {"border-serapide bg-serapide": checked, checked})}></label>
                </div> ) } 
            </div>
            {isFunction(children) && children(checked)}
        </React.Fragment>) : null
    }
export default Switch

const showError = (error, onError) => {
    toast.error(error.message,  {autoClose: true})
}
const _getInput = () => ({variables: {input: {}}})

export const EnhancedSwitch  = ({isLocked, mutation, update, getInput = _getInput, label, value = false, className, children, checked, labelClassName, ignoreChecked = false, ...mutationProps}) => {
    return (
    <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
        {(onChange, m_props) => {
            const toggleSwitch = (checked, val) => {
                if (checked || ignoreChecked) {
                    onChange(getInput(val))
                }
            }
            return (
                <Switch isLocked={isLocked} toggleSwitch={toggleSwitch} label={label} value={value} className={className} children={children} checked={checked} labelClassName={labelClassName}/>
            )
        }}
    </Mutation>)
}

export const UnSwitch = enhancer(Switch)
