/*
 * Copyright 2019, GeoSolutions SAS.
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
 * Simple btn with icon, label central aligned  and spinner on the right
 * 
 **/ 
export default ({label = "", iconSize, icon = "", fontSize= "size-12", classNameLabel = "py-2", spinnerClass = "spinner-border spinner-border-sm ml-2", isLoading = false, ...props}) => (
    <Button {...props}>
        <span className={`${classNameLabel} ${fontSize} d-flex align-items-center justify-content-around`} >
            <i className={`material-icons ${iconSize && iconSize}`}>{icon}</i>
            <span className="pl-1">{label}</span>
            {isLoading && (<div className={spinnerClass} role="status">
                <span className="sr-only">Loading...</span>
            </div>)}
        </span>
    </Button>

)