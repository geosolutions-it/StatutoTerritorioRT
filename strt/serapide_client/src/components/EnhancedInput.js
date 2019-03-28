// Pass a mutation an update function if needed, the getInput

import React from 'react'
import {Input} from 'reactstrap'
import "react-datepicker/dist/react-datepicker.css"
import {Mutation} from  "react-apollo"
import {showError} from '../utils'
import {debounce} from 'lodash'


const updatePiano = (update, getInput, value) => {
    update(getInput(value))
}
const debounced = debounce(updatePiano, 500)

export default  ({className, disabled, mutation, value, update, selected, type="textarea", placeholder, getInput = (val) => { return {variables: {input: {descrizione: val}}}}, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
            {(onChange, m_props) => {
                const saveInput = (e) => {
                    const value = e.target.value;
                    debounced(onChange, getInput, value)
                }
                return (
                <Input className={className} disabled={disabled} onChange={saveInput} type={type} name="text" defaultValue={value} placeholder={placeholder}/>
                )
            }}
        </Mutation>)
}

