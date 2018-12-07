/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from 'react'
import {
    Button
} from 'reactstrap'


/**
 * Simple btn with icon and label central aligned  
 * 
 **/ 
export default ({label = "", icon = "", ...props}) => (
    <Button {...props}>
        <span className="d-flex align-items-center">
        <i className="material-icons">{icon}</i>{label}</span>
    </Button>

)