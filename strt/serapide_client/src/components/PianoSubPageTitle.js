/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


export default ({icon, title, iconClassName="material-icons icon-30 text-white bg-serapide p-2 mr-2 rounded-circle"}) => (
    <span className="d-flex align-items-center justify-content-center mb-5" >
        <i className={iconClassName}>{icon}</i>
        <div className="size-26">{title}</div>
    </span>
    )

