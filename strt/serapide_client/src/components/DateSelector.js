/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css"
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'
import Button from 'components/IconButton'

const _getInput = (val) => { return {variables: {input: {data: val.toISOString()}}}}
const cleanClassName = (className = "") => className.split(" ").filter( c => !c.startsWith("icon-") && !c.startsWith("size-")).join(" ")
const getIconSizeClass = (className = "" ) => className.split(" ").filter( c => c.startsWith("icon-")).pop()
const getFontSizeClass = (className = "" ) => className.split(" ").filter( c => c.startsWith("size-")).pop()
class CustomInput extends React.PureComponent {
    render () {
        const {onClick, value, disabled, readOnly, className, placeholder} = this.props 
        
        return (
                <Button 
                    iconSize={getIconSizeClass(className)}
                    fontSize={getFontSizeClass(className)}
                    disabled={disabled}
                    className={`${readOnly && 'read-only'} ${cleanClassName(className)}`}
                    label={value || placeholder}
                    color="serapide"
                    icon="date_range"
                    onClick={onClick}>          
                </Button>
            )
    }
  }

class DateTimeInput extends React.PureComponent {
    render () {
        const {onClick, value = ""} = this.props 
        const data = value.trim().split(" ").slice(0, 1).pop()
        const ora = value.trim().split(" ").slice(1).join(" ")
            return (
                <div className="row flex-fill p-2 text-serapide border pointer"
                onClick={onClick}>
                    <div className="col-6">{data || "Data"}</div>
                    <div className="col-6">{ora || "Ora"}</div>
    
                </div>)
    }
  }

const showError = (error, onError) => {
    toast.error(error.message,  {autoClose: true})
}

export default (props) => (<DatePicker customInput={<CustomInput />} {...props}/>) 

// Pass a mutation an update function if needed, the getInput
export const EnhancedDateSelector = ({placeholder = "Seleziona Data", popperPlacement, useDateTime = false, showTimeSelect = false, className, isLocked, mutation, update, selected, disabled, iconSize, getInput = _getInput, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
            {(onChange, m_props) => {
                const saveDate = (val) => {
                    onChange(getInput(val))
                }
                return (
                    <DatePicker
                    popperPlacement={popperPlacement}
                    placeholderText={placeholder}
                    calendarClassName={useDateTime ? "d-flex" : undefined}
                    showTimeSelect={showTimeSelect}
                    readOnly={isLocked}
                    className={className}
                    disabled={disabled}
                    selected={selected}
                    iconSize={iconSize}
                    customInput={useDateTime ? <DateTimeInput/> : <CustomInput />}
                    onChange={saveDate}
                    timeFormat="HH:mm"
                    timeIntervals={15}
                    dateFormat={useDateTime ? "dd-MM-yyyy h:mm aa" : "dd-MM-yyyy" }/>
                )
            }}
        </Mutation>)
}

