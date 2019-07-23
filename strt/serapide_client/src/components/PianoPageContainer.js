/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


export default ({children = [], className}) => (
    <div className="d-flex border-top pb-4">
        <div className={`piano-page-content border flex-fill ${className}`}>
            {children}
        </div>
    </div>
    )