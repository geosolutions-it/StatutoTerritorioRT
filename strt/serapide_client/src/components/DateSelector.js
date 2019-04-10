/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Button from '../components/IconButton'
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css"
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'

const _getInput = (val) => { return {variables: {input: {data: val.toISOString()}}}}

class CustomInput extends React.PureComponent {
    render () {
        const {onClick, value, disabled, readOnly, className, placeholder} = this.props 
            return (
                <Button 
                    disabled={disabled}
                    className={`${readOnly && 'read-only'} ${className}`}
                    style={{minWidth: 170}}
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
        const {onClick, value = "", disabled, readOnly, className} = this.props 
        const data = value.trim().split(" ").slice(0, 1).pop()
        const ora = value.trim().split(" ").slice(1).join(" ")
        console.log(value)
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
export const EnhancedDateSelector = ({placeholder = "Seleziona Data", useDateTime = false, showTimeSelect = false, className, isLocked, mutation, update, selected, disabled, getInput = _getInput, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
            {(onChange, m_props) => {
                const saveDate = (val) => {
                    onChange(getInput(val))
                }
                return (
                    <DatePicker
                    placeholderText={placeholder}
                    calendarClassName={useDateTime ? "d-flex" : undefined}
                    showTimeSelect={showTimeSelect}
                    readOnly={isLocked}
                    className={className}
                    disabled={disabled}
                    selected={selected}
                    customInput={useDateTime ? <DateTimeInput/> : <CustomInput />}
                    onChange={saveDate}
                    timeFormat="HH:mm"
                    timeIntervals={15}
                    dateFormat={useDateTime ? "dd-MM-yyyy h:mm aa" : "dd-MM-yyyy" }/>
                )
            }}
        </Mutation>)
}

