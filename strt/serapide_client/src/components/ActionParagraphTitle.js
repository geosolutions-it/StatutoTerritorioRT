/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


export default ({label, children, fontWeight ="font-weight-bold", className = "size-14 pb-1"}) => (
    <div  className={`pt-5 ${fontWeight || ''} ${className || ''}`}>
        {children ? children : label}
    </div>
    )