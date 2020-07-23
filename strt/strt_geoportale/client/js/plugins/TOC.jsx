/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React, { useState } from 'react';
import { connect } from 'react-redux';
import { Nav, NavItem } from 'react-bootstrap';
import { selectNode } from '@mapstore/actions/layers';
import { createPlugin } from '@mapstore/utils/PluginsUtils';
import { TOCPlugin as MSTOCPlugin, reducers, epics } from '@mapstore/plugins/TOC';
import PropTypes from 'prop-types';
import HeaderNode from '@js/plugins/toc/HeaderNode';
import GroupNode from '@js/plugins/toc/GroupNode';
import LayerNode from '@js/plugins/toc/LayerNode';

function TOC({
    activateRemoveLayer = false,
    activateRemoveGroup = false,
    activateAddLayerButton = false,
    activateAddGroupButton = false,
    activateSettingsTool = false,
    activateSortLayer = false,
    tocGroups = [
        {
            id: 'piano',
            label: 'Piano',
            include: ['piano']
        },
        {
            id: 'risorse_rt',
            label: 'Risorse RT',
            include: ['risorse_rt']
        },
        {
            id: 'invarianti',
            label: 'Invarianti',
            include: ['invarianti']
        },
        {
            id: 'basi_cartografiche',
            label: 'Cartografia di base',
            include: ['basi_cartografiche']
        }
    ],
    onSelectNode,
    ...props
}) {
    // get button of serapide project from others plugin
    const buttons = props.items
        .filter(({ serapideButton }) => serapideButton)
        .map(({ serapideButton: Tool, name }) => <Tool key={name}/> );

    const [selected, setSelected] = useState(tocGroups[0]);

    return (
        <div className="ms-toc">
            <Nav
                justified
                stacked
                bsSize="sm"
            >
                {tocGroups.map((entry) =>
                    <NavItem
                        key={entry.id}
                        className={'ms-group-' + entry.id}
                        active={selected.id === entry.id}
                        onClick={() => {
                            setSelected(entry);
                            // deselect layers on change tab
                            onSelectNode();
                        }}>
                        {entry.label}
                    </NavItem>)}
            </Nav>

            <MSTOCPlugin
                { ...props }
                activateRemoveLayer={activateRemoveLayer}
                activateRemoveGroup={activateRemoveGroup}
                activateAddLayerButton={activateAddLayerButton}
                activateAddGroupButton={activateAddGroupButton}
                activateSettingsTool={activateSettingsTool}
                activateSortLayer={activateSortLayer}
                layerNodeComponent={LayerNode}
                groupNodeComponent={(groupNodeProps) =>
                    <GroupNode
                        { ...groupNodeProps }
                        headerButtons={selected.id === 'piano' && buttons || undefined}
                        filterHeaderNode={node => {
                            return selected?.include.indexOf(node.id) !== -1;
                        }}
                        replaceComponent={({ level })=> level === 1 ? HeaderNode : null}
                    />}
            />
        </div>
    );
}

TOC.contextTypes = {
    loadedPlugins: PropTypes.object
};

export default createPlugin('TOC', {
    component: connect(() => ({}), {
        onSelectNode: selectNode
    })(TOC),
    containers: {
        DrawerMenu: {
            name: 'toc',
            position: 1,
            glyph: "1-layer",
            buttonConfig: {
                buttonClassName: "square-button no-border",
                tooltip: "toc.layers"
            },
            priority: 2
        }
    },
    reducers,
    epics
});
