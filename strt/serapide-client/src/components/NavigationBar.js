/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem
} from 'reactstrap';
import LinkWithIcon from './LinkWithIcon'
import UserMenu from './UserMenu'
export default class Example extends React.Component {
  constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);
    this.state = {
      isOpen: false
    };
  }
  toggle() {
    this.setState({
      isOpen: !this.state.isOpen
    });
  }
  render() {
    return (
        <Navbar className="serapide-top-offset pr-1" color="dark" dark  expand="sm" fixed="top">
          <NavbarBrand className="text-white">
                  <span className="d-none d-lg-inline-block pl-2">
                  COMUNE DI SCANDICCI</span>
          </NavbarBrand>
          <NavbarToggler onClick={this.toggle} />
          <Collapse isOpen={this.state.isOpen} navbar>
            <Nav className="ml-auto text-center" navbar>
              <NavItem>
                <LinkWithIcon className="vertical-divider-left" icon="find_in_page" label="Ricerca" link="./#/search"></LinkWithIcon>
              </NavItem>
              <NavItem>
                <LinkWithIcon icon="view_list" label="Archivio Piani" link="./#/archivio"></LinkWithIcon>
              </NavItem>
              <NavItem>
                <LinkWithIcon className="vertical-divider-right" icon="note_add" label="Crea Nuovo Piano" link="./#/nuovo_piano"></LinkWithIcon>
              </NavItem>
              <NavItem>
                <LinkWithIcon className="vertical-divider-right" icon="today" label="Calendario" link="./#/nuovo_piano"></LinkWithIcon>
              </NavItem>
              <NavItem>
                <LinkWithIcon icon="notification_important" iconColor="text-danger" withBadge badge="10" label="Alert" link="#"></LinkWithIcon>
              </NavItem>
              <NavItem>
                <LinkWithIcon className="vertical-divider-right" icon="email" iconColor="text-warning" withBadge badge="5" link="#"label="Messaggi"></LinkWithIcon>
              </NavItem>
              <UserMenu></UserMenu>
            </Nav>
          </Collapse>
        </Navbar>
    );
  }
}