/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


export default ({label, children, className}) => (
    <div  className={`pt-4 font-weight-light ${className}`}>
        {children ? children : label}
    </div>
    )