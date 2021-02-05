/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { Component, cloneElement, memo } from 'react';
import PropTypes from 'prop-types';
import GroupChildren from '@mapstore/components/TOC/fragments/GroupChildren';
import { getTitleAndTooltip } from '@mapstore/utils/TOCUtils';
import Filter from '@mapstore/components/misc/Filter';
import Message from '@mapstore/components/I18N/Message';
import { Button } from 'react-bootstrap';

const replaceNodeOptions = (currentNode, nodeType, filterText) => {
    if (nodeType === 'group' && filterText) {
        return {
            ...currentNode,
            expanded: true
        };
    }
    return currentNode;
};


const loopFilter = ({ node, filterText, currentLocale }) => {
    return !!node?.nodes?.find((nd) => {
        if (nd.nodes) {
            return loopFilter({ node: nd, filterText, currentLocale });
        }
        if (nd.dummy) {
            return false;
        }
        const { title: currentTitle } = getTitleAndTooltip({ node: nd, currentLocale });
        return currentTitle.toLowerCase().indexOf(filterText.toLocaleLowerCase()) !== -1;
    });
};

/**
 * Node header for table of content
 * @class
 * @name HeaderNode
 * @prop {string} node
 * @prop {number} level level of nested group
 * @prop {func} onSort event triggered after sorting event
 * @prop {func} onError event triggered after error event from group children
 * @prop {string} currentLocale selected language locale
 * @prop {func} setDndState set drag and drop state
 */
class HeaderNode extends Component {

    static propTypes = {
        node: PropTypes.object,
        level: PropTypes.number,
        onSort: PropTypes.func,
        onError: PropTypes.func,
        currentLocale: PropTypes.string,
        setDndState: PropTypes.func,
        filterHeaderNode: PropTypes.func,
        getHeaderButtons: PropTypes.func,
        onUpdateNode: PropTypes.func
    };

    static defaultProps = {
        node: {},
        level: 1,
        currentLocale: 'en-US',
        filterHeaderNode: () => true,
        getHeaderButtons: () => null
    };

    state = {
        filterText: ''
    };

    render() {

        const {
            node,
            level,
            onSort,
            onError,
            currentLocale,
            setDndState,
            children,
            filterHeaderNode,
            getHeaderButtons,
            onUpdateNode
        } = this.props;

        if (!filterHeaderNode(node)) {
            return null;
        }

        const headerButtons = getHeaderButtons(node);

        const { filterText } = this.state;

        const { title } = getTitleAndTooltip({ node, currentLocale });

        const groupChildren = children && (
            <GroupChildren
                node={node}
                level={level + 1}
                onSort={onSort}
                onError={onError}
                setDndState={setDndState}
                position="collapsible">
                {cloneElement(children, {
                    filterText,
                    emptyMessageId: node.id === 'piano' && 'serapide.pianoNoLayer',
                    replaceNodeOptions: (currentNode, nodeType) => replaceNodeOptions(currentNode, nodeType, filterText),
                    filter: (currentNode, nodeType) => {
                        if (nodeType === 'group' && filterText) {
                            return loopFilter({ node: currentNode, filterText, currentLocale });
                        }
                        if (nodeType === 'layer' && filterText) {
                            const { title: currentTitle } = getTitleAndTooltip({ node: currentNode, currentLocale });
                            return currentTitle.toLowerCase().indexOf(filterText.toLocaleLowerCase()) !== -1;
                        }
                        return true;
                    }
                })}
            </GroupChildren>
        );

        const isEmpty = !loopFilter({ node, filterText, currentLocale });
        // only direct groups child should be toggle with the collapse/expand all button
        const hasGroupsChild = !!node?.nodes?.find(({ nodes }) => nodes);
        const expanded = !!(hasGroupsChild && node.nodes
            .find((nestedNode) => nestedNode.nodes
                ? nestedNode.expanded === undefined ? true : nestedNode.expanded
                : nestedNode.expanded
            ));
        return (
            <div
                className={'ms-header-node ms-group-' + node.id}>
                <div className="ms-header-node-title"><div>{title}</div>{headerButtons}</div>
                {node?.description && <div className="ms-header-node-description">{node.description}</div>}
                {node?.caption && <div className="ms-header-node-caption">{node.caption}</div>}
                <Filter
                    filterText={filterText}
                    onFilter={(newFilterText) => this.setState({ filterText: newFilterText })}
                />
                {isEmpty && <div className="ms-nodes-empty">
                    <Message msgId={!filterText ? 'noLayerInGroup' : 'noLayerFilterResults'}/>
                </div>}
                {hasGroupsChild && <Button
                    bsSize="xs"
                    className="ms-header-node-toggle-expanded"
                    onClick={() => {
                        node.nodes.forEach((nestedNode) => {
                            const nodeExpanded = nestedNode.expanded === undefined ? true : nestedNode.expanded;
                            if (nestedNode.nodes && nodeExpanded === expanded) {
                                onUpdateNode(
                                    nestedNode.id,
                                    'groups',
                                    { expanded: !expanded }
                                );
                            }
                        });
                    }}
                >
                    <Message msgId={expanded ? 'serapide.collapseAll' : 'serapide.expandAll'}/>
                </Button>}
                {groupChildren}
            </div>
        );
    }
}

export default memo(HeaderNode);
