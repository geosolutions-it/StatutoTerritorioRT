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
        const {onClick, value, disabled, readOnly, className} = this.props 
            return (
                <Button 
                    disabled={disabled}
                    className={`${readOnly && 'read-only'} ${className}`}
                    style={{minWidth: 170}}
                    label={value || "Seleziona Data"}
                    color="serapide"
                    icon="date_range"
                    onClick={onClick}>          
                </Button>
            )
    }
  }

const showError = (error, onError) => {
    toast.error(error.message,  {autoClose: true})
}

export default (props) => (<DatePicker customInput={<CustomInput />} {...props}/>) 

// Pass a mutation an update function if needed, the getInput
export const EnhancedDateSelector = ({isLocked, mutation, update, selected, disabled, getInput = _getInput, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
            {(onChange, m_props) => {
                const saveDate = (val) => {
                    onChange(getInput(val))
                }
                return (
                    <DatePicker readOnly={isLocked} disabled={disabled} selected={selected} customInput={<CustomInput />} onChange={saveDate}/>
                )
            }}
        </Mutation>)
}

