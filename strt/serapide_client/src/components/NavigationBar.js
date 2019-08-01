/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import {
  NavItem
} from 'reactstrap';
import LinkWithIcon from './LinkWithIcon'

import Messaggi from './MenuMessaggi'
import {toggleControllableState} from 'enhancers'
import classNames from "classnames"

export default toggleControllableState("isOpen", "toggle", false) (({roleType, attore, isOpen= false, toggle = () =>{}, user = {}, messaggi = [], alertsCount = 0}) => (
            <React.Fragment>
              <NavItem className="first">
                <LinkWithIcon className="vertical-divider-left disabled" icon="find_in_page" label="Ricerca" link="/serapide/#/search" disabled></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon className="disabled" icon="view_list" label="Archivio Piani" link="/serapide/#/archivio" disabled></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon className={classNames("vertical-divider-right", {disabled: !(roleType === "RUP" && attore === "Comune")})} disabled={!(roleType === "RUP" && attore === "Comune")} icon="note_add" label="Crea Nuovo Piano" link="/serapide/#/nuovo_piano"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon className="vertical-divider-right disabled"  disabled icon="today" label="Calendario"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon  className="default" link="./#/" icon="notification_important" iconColor="text-danger" withBadge badge={alertsCount} label="Alert"></LinkWithIcon>
              </NavItem>
              <Messaggi className="first" messaggi={messaggi}></Messaggi>
            </React.Fragment>
))