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





const enhancers = withControllableState('section', 'toggleSection', 'adozione')


export default enhancers( ({risorseAdozione=[], risorseControdeduzioni=[], risorsePostCP=[], section, toggleSection}) => {
    return (
        <React.Fragment>
        <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'adozione' })}
                        onClick={() => { toggleSection('adozione'); }}>
                        TRASMISSIONE
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames({ active: section === 'controdedotto' })}
                        onClick={() => { toggleSection('controdedotto'); }}>
                        CONTRODEDOTTO
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
                <TabPane tabId="adozione">
                    <Elaborati upload={false} resources={risorseAdozione}></Elaborati>
                </TabPane>
                <TabPane tabId="controdedotto">
                    <Elaborati upload={false} resources={risorseControdeduzioni}></Elaborati>
                </TabPane>
                <TabPane tabId="revisionePostCp">
                    <Elaborati upload={false} resources={risorsePostCP}></Elaborati>
                </TabPane>
            </TabContent>
            </React.Fragment>
    )



})