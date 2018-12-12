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
export default ({label = "", icon = "", fontSize= "80%",...props}) => (
    <Button {...props}>
        <span className="py-2 d-flex align-items-center" style={{fontSize}}>
            <i className="material-icons">{icon}</i>
            <span>{label}</span>
        </span>
    </Button>

)