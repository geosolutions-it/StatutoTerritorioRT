/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import {
    Badge } from 'reactstrap';

export default ({link = "", icon = "", iconColor = "",  label = "", className="", withBadge = false, badge = ""}) => {
    return (
            <a className={`${className} link-icon nav-link`} href={link}>
            {withBadge ? ( 
                <span className="d-inline-flex align-items-center">
                    <i className={`material-icons ${iconColor}`}>{icon}</i>
                    <Badge className="nav-btn-badge" color="light">{badge}</Badge>
                </span>) : (<i className={`material-icons ${iconColor}`}>{icon}</i>)
            }
                <div className="link-icon-label">{label}</div>

            </a>
    )
}