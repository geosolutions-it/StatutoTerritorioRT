/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import Select from 'react-select'
const options = [
    { value: 'po', label: 'Piano Operativo' },
    { value: 'ps', label: 'Piano Strutturale' },
    { value: 'var', label: 'Variante' }
  ]
export default () => (
    <Select 
        defaultValue={options[0]}
        options={options} classNamePrefix="tipo">
    </Select>)