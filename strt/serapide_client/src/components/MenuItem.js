/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import classNames from 'classnames'
import {withRouter} from "react-router-dom"
export default withRouter(({title, subtitle, icon, disabled = false, iconColor, active = false, locked = false, className = "", expanded = false, children, href, history}) => {
    return (
    <li onClick={() => { if(href) history.push(href)}} className={classNames("list-group-item", className, {"text-serapide": active, active, locked, collapsed: !expanded})}>
        <div  data-for="sidebar-tooltip" data-tip-disable={expanded} data-tip={title} className="d-flex align-items-center icons">
            {locked && expanded  && (<i className="material-icons icon-12">lock</i>)}
            <i className={classNames("material-icons", {"icon-16": !expanded}, iconColor)}>{icon}</i>
        </div>
        {expanded && (
        <div className="d-flex flex-column">
            <span className="title">{title}</span>
            <span className="sub-title">{subtitle}</span>
        </div>)}
        {expanded && children}
    </li>
)})