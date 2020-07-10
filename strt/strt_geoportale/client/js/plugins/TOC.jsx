/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React from 'react';
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
    ...props
}) {
    // get button of serapide project from others plugin
    const buttons = props.items
        .filter(({ serapideButton }) => serapideButton)
        .map(({ serapideButton: Tool, name }) => <Tool key={name}/> );

    return (
        <div className="ms-toc">
            <div className="ms-toc-tools">{buttons}</div>
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
    component: TOC,
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
