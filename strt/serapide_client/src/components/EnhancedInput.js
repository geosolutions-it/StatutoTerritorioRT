// Pass a mutation an update function if needed, the getInput

import React from 'react'
import {Input} from 'reactstrap'
import "react-datepicker/dist/react-datepicker.css"
import {Mutation} from  "react-apollo"
import {showError} from 'utils'
import {debounce} from 'lodash'


const updatePiano = (update, getInput, value) => {
    update(getInput(value))
}
const debounced = debounce(updatePiano, 500)

export default  ({className, rows, disabled, mutation, value, update, selected, type="textarea", placeholder, getInput = (val) => { return {variables: {input: {descrizione: val}}}}, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} onError={showError} update={update} {...mutationProps}>
            {(onChange, {error}) => {
                const saveInput = (e) => {
                    const value = e.target.value;
                    debounced(onChange, getInput, value)
                }
                return (
                <Input rows={rows} className={className} invalid={error} disabled={disabled} onChange={saveInput} type={type} name="text" defaultValue={error ? '' : value} placeholder={placeholder}/>
                )
            }}
        </Mutation>)
}

