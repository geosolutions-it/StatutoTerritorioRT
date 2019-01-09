/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Select from 'react-select'
import {branch, renderComponent} from 'recompose'

const getOptionLabel = ({node: {type: {tipo} = {}, name} = {}}) => `${tipo} - ${name}`
const getOptionValue = ({node: {code} = {}}) => code

const Comune = ({className, enti = [], value: {node: {code, type: {tipo} = {}} ={}} = {}, onChange = () =>{}, isLoading = false}) => (
        <span className={`${className} d-flex flex-row justify-content-between text-uppercase`}>
            <span>{`id ${tipo} ${code}`}</span>
            {enti.length > 1 && (<span className="link-icon" onClick={() => onChange()}>X</span>)}
        </span>)

const Comuni = ({ value, onChange = () => {}, className, enti, isLoading = false}) => (
            <Select 
                getOptionLabel={getOptionLabel}
                getOptionValue={getOptionValue}
                placeholder="Selezionare ente"
                onChange={onChange}
                value={value}  className={className}
                options={enti} classNamePrefix="tipo"
                isLoading={isLoading}>
            </Select>)

export default branch(({enti= [], value}) => !value, renderComponent(Comuni), renderComponent(Comune))((() => null))