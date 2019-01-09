/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Select from 'react-select'

export default ({ value, onChange= (val,action) => {}, className, error, isLoading = false, tipiPiano= []}) => (
            <Select 
                    placeholder="Selezionare il tipo piano..."
                    isDisabled={!!error}
                    onChange={onChange}
                    value={value}  isLoading={isLoading} className={className}
                    options={tipiPiano} classNamePrefix="tipo"
                    filter>
            </Select>)
