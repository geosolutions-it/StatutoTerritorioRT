// Pass a mutation an update function if needed, the getInput

import React from 'react'
import {Input} from 'reactstrap'
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css"
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'
import {debounce} from 'lodash'


const updatePiano = (update, getInput, value) => {
    update(getInput(value))
}
const debounced = debounce(updatePiano, 500)


const showError = (error, onError) => {
    toast.error(error.message,  {autoClose: true})
}


export default  ({mutation, value, update, selected, getInput = (val) => { return {variables: {input: {descrizione: val}}}}, ...mutationProps}) => {
    return (
        <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
            {(onChange, m_props) => {
                const saveInput = (e) => {
                    const value = e.target.value;
                    debounced(onChange, getInput, value)
                }
                return (
                <Input onChange={saveInput} type="textarea" name="text" defaultValue={value}/>
                )
            }}
        </Mutation>)
}

