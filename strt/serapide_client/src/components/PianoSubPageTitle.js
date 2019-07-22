/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


export default ({icon, title, iconClassName="material-icons icon-34 text-white bg-serapide p-2 mr-2 rounded-circle"}) => (
    <span className="d-flex justify-content-center" >
        <i className={iconClassName}>{icon}</i>
        <div className="size-28">{title}</div>
    </span>
    )

