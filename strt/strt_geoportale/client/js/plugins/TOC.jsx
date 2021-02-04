/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { createSelector } from 'reselect';
import { Nav, NavItem } from 'react-bootstrap';
import { selectNode, removeLayer } from '@mapstore/actions/layers';
import { selectedNodesSelector } from '@mapstore/selectors/layers';
import { createPlugin } from '@mapstore/utils/PluginsUtils';
import { TOCPlugin as MSTOCPlugin, reducers, epics } from '@mapstore/plugins/TOC';
import PropTypes from 'prop-types';
import HeaderNode from '@js/plugins/toc/HeaderNode';
import GroupNode from '@js/plugins/toc/GroupNode';
import LayerNode from '@js/plugins/toc/LayerNode';
import url from 'url';

const ConnectedLayerNode = connect(() => ({
    enableInlineRemove: node => !!(node?.group === 'Default' || node?.group === undefined)
}), {
    onRemove: removeLayer
})(LayerNode);

function TOC({
    activateRemoveLayer = false,
    activateRemoveGroup = false,
    activateAddLayerButton = false,
    activateAddGroupButton = false,
    activateSettingsTool = false,
    activateSortLayer = false,
    defaultSelectedGroup,
    tocGroups = [
        {
            id: 'piano',
            label: 'Piano',
            include: ['piano', 'Default']
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
    isNodeSelected,
    onSelectNode,
    ...props
}) {
    // get button of serapide project from others plugin
    const buttons = props.items
        .filter(({ serapideButton }) => serapideButton)
        .map(({ serapideButton: Tool, name }) => <Tool key={name}/> );

    const [selected, setSelected] = useState(defaultSelectedGroup || tocGroups[0]);

    useEffect(() => {
        if (defaultSelectedGroup) {
            setSelected(defaultSelectedGroup);
        }
    }, [defaultSelectedGroup]);

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
                            if (isNodeSelected) {
                                onSelectNode();
                            }
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
                layerNodeComponent={ConnectedLayerNode}
                groupNodeComponent={(groupNodeProps) =>
                    <GroupNode
                        { ...groupNodeProps }
                        getHeaderButtons={(node) => node.id === 'piano' && buttons || undefined}
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

function getTocGroups(state) {
    const search = state?.router?.location?.search;
    const defaultMaps = state?.serapide?.defaultMaps;
    const { query = {} } = search && url.parse(search, true) || {};
    if (query.static && defaultMaps) {
        const { tocGroups = null, selectedGroup = undefined } = defaultMaps.find(({ id }) => id === query.static) || {};
        const defaultSelectedGroup = tocGroups?.find(({ id }) => selectedGroup === id);
        return { tocGroups, defaultSelectedGroup };
    }
    return { tocGroups: null, defaultSelectedGroup: undefined };
}

export default createPlugin('TOC', {
    component: connect(
        createSelector([getTocGroups, selectedNodesSelector], ({ tocGroups, defaultSelectedGroup }, selectedNodes) => ({
            tocGroups,
            defaultSelectedGroup,
            isNodeSelected: !!(selectedNodes?.length > 0)
        })),
        { onSelectNode: selectNode },
        (stateProps, dispatchProps, ownProps) => ({
            ...ownProps,
            ...stateProps,
            ...dispatchProps,
            tocGroups: stateProps.tocGroups
                ? stateProps.tocGroups
                : ownProps.tocGroups
        })
    )(TOC),
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
