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


export default enhancers( ({risorseAdozione=[], risorseControdeduzioni=[], risorsePostCP=[], section, toggleSection, ...props}) => {
    return (
        <React.Fragment>
        <Nav tabs>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'adozione' }])}
                        onClick={() => { toggleSection('adozione'); }}>
                        TRASMISSIONE
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'controdedotto' }])}
                        onClick={() => { toggleSection('controdedotto'); }}>
                        CONTRODEDOTTO
                    </NavLink>
                </NavItem>
                <NavItem>
                    <NavLink
                        className={classnames(["pointer", { active: section === 'revisionePostCp' }])}
                        onClick={() => { toggleSection('revisionePostCp'); }}>
                        POST C.P.
                    </NavLink>
                </NavItem>
            </Nav>
            <TabContent activeTab={section}>
                <TabPane tabId="adozione">
                    {risorseAdozione.length > 0 ? <Elaborati upload={false} resources={risorseAdozione} {...props}></Elaborati> : (<div className="mt-2 py-2">Nessun elaborato presente</div>) }
                </TabPane>
                <TabPane tabId="controdedotto">
                {risorseControdeduzioni.length>0 ? <Elaborati upload={false} resources={risorseControdeduzioni} {...props}></Elaborati>  : (<div className="mt-2 py-2">Nessun elaborato presente</div>) }
                </TabPane>
                <TabPane tabId="revisionePostCp">
                    {risorsePostCP.length > 0 ? <Elaborati upload={false} resources={risorsePostCP} {...props}></Elaborati> : (<div className="mt-2 py-2">Nessun elaborato presente</div>) }
                </TabPane>
            </TabContent>
            </React.Fragment>
    )



})