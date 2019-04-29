/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Nav, NavItem,NavLink, TabContent,TabPane} from 'reactstrap'

import Elaborati from "./ElaboratiPiano"

import classnames from 'classnames'
import {withControllableState} from 'enhancers'





const enhancers = withControllableState('section', 'toggleSection', 'approvazione')


export default enhancers( ({risorseApprovazione=[], risorsePostCP=[], section, toggleSection}) => {
    return (
        <React.Fragment>
        <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'approvazione' })}
                        onClick={() => { toggleSection('approvazione'); }}>
                        TRASMISSIONE
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'revisionePostCp' })}
                        onClick={() => { toggleSection('revisionePostCp'); }}>
                        POST C.P.
                    </NavLink>
                </NavItem>
            </Nav>
            <TabContent activeTab={section}>
                <TabPane tabId="approvazione">
                    <Elaborati upload={false} resources={risorseApprovazione}></Elaborati>
                </TabPane>
                <TabPane tabId="revisionePostCp">
                    <Elaborati upload={false} resources={risorsePostCP}></Elaborati>
                </TabPane>
            </TabContent>
            </React.Fragment>
    )



})