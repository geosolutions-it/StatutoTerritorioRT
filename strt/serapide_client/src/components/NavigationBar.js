/*
 * Copyright 2018, GeoSolutions Sas.
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
import {toggleControllableState} from '../enhancers/utils'


export default toggleControllableState("isOpen", "toggle", false) (({isOpen= false, toggle = () =>{}, user = {}, messaggi = [], alertsCount = 0}) => (
            <React.Fragment>
              <NavItem className="first">
                <LinkWithIcon className="vertical-divider-left" icon="find_in_page" label="Ricerca" link="./#/search"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon icon="view_list" label="Archivio Piani" link="./#/archivio"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon className="vertical-divider-right" icon="note_add" label="Crea Nuovo Piano" link="./#/nuovo_piano"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon className="vertical-divider-right" icon="today" label="Calendario"></LinkWithIcon>
              </NavItem>
              <NavItem className="first">
                <LinkWithIcon  link="./#/" icon="notification_important" iconColor="text-danger" withBadge badge={alertsCount} label="Alert"></LinkWithIcon>
              </NavItem>
              <Messaggi className="first" messaggi={messaggi}></Messaggi>
            </React.Fragment>
))