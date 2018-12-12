/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem } from 'reactstrap'

export default ({disabled, user= {}}) => (
    <UncontrolledDropdown className="usermenu text-white" inNavbar>
    <DropdownToggle  className={`${disabled ? "disabled" : ""} p-0`} nav caret disabled={disabled}>
            <span className="link-icon d-inline-flex flex-row">
                <i className="material-icons text-warning m-1 rounded-circle bg-white">person</i>
                <div className="flex-column align-self-center">
                  <div className="link-icon-label ">{user.nome}</div>
                </div> 
            </span>
    </DropdownToggle>
    <DropdownMenu right>
    <DropdownItem className="text-warning text-uppercase" header>{`ruolo: ${user.ruolo || ''}`}</DropdownItem>
      <DropdownItem tag="a" href="/users/user-profile/">Profilo</DropdownItem>
      <DropdownItem tag="a" href="">Impostazioni</DropdownItem>
      <DropdownItem tag="a" href="/users/logout/">Logout</DropdownItem>
    </DropdownMenu>
  </UncontrolledDropdown>
)