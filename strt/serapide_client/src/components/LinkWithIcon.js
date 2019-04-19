/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import {
    Badge } from 'reactstrap';

export default ({disabled = false, link, icon = "", iconColor = "",  label = "", className="", withBadge = false, badge = ""}) => {
    const El = link ? "a" : "span";
    return (
            <El className={`${className} link-icon nav-link`} href={!disabled ? link : "" }>
            {withBadge ? ( 
                <span className="d-inline-flex align-items-center">
                    <i className={`material-icons ${iconColor}`}>{icon}</i>
                    <Badge className="nav-btn-badge" color="light">{badge}</Badge>
                </span>) : (<i className={`material-icons ${iconColor}`}>{icon}</i>)
            }
                <div className="link-icon-label">{label}</div>

            </El>
    )
}