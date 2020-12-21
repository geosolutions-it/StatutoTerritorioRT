/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { Component, cloneElement, memo } from 'react';
import Node from '@mapstore/components/TOC/Node';
import PropTypes from 'prop-types';
import draggableComponent from '@mapstore/components/TOC/enhancers/draggableComponent';
import GroupChildren from '@mapstore/components/TOC/fragments/GroupChildren';
import { getTitleAndTooltip } from '@mapstore/utils/TOCUtils';
import SideCard from '@mapstore/components/misc/cardgrids/SideCard';
import Toolbar from '@mapstore/components/misc/toolbar/Toolbar';
import ReactTooltip from 'react-tooltip';
import Portal from '@mapstore/components/misc/Portal';
import Message from '@mapstore/components/I18N/Message';
import { InView } from 'react-intersection-observer';

export class GroupNode extends Component {

    static propTypes = {
        node: PropTypes.object,
        style: PropTypes.object,
        onToggle: PropTypes.func,
        level: PropTypes.number,
        onSort: PropTypes.func,
        onError: PropTypes.func,
        propertiesChangeHandler: PropTypes.func,
        currentLocale: PropTypes.string,
        selectedNodes: PropTypes.array,
        onSelect: PropTypes.func,
        titleTooltip: PropTypes.bool,
        tooltipOptions: PropTypes.object,
        setDndState: PropTypes.func,
        connectDragSource: PropTypes.func,
        connectDragPreview: PropTypes.func,
        connectDropTarget: PropTypes.func,
        isDraggable: PropTypes.bool,
        isDragging: PropTypes.bool,
        isOver: PropTypes.bool,
        replaceComponent: PropTypes.bool,
        filter: PropTypes.func,
        replaceNodeOptions: PropTypes.func,
        filterText: PropTypes.string,
        emptyMessageId: PropTypes.string
    };

    static defaultProps = {
        node: {},
        style: {},
        onToggle: () => {},
        propertiesChangeHandler: () => {},
        level: 1,
        currentLocale: 'en-US',
        selectedNodes: [],
        onSelect: () => {},
        titleTooltip: false,
        connectDragPreview: (cmp) => cmp,
        connectDragSource: (cmp) => cmp,
        connectDropTarget: (cmp) => cmp,
        isDraggable: false,
        isDragging: false,
        isOver: false,
        replaceComponent: () => null,
        filter: () => true
    };

    renderNode(inView) {
        const {
            node: nodeProp,
            style,
            onToggle,
            level,
            onSort,
            onError,
            propertiesChangeHandler,
            currentLocale,
            selectedNodes,
            onSelect,
            titleTooltip,
            // tooltipOptions,
            setDndState,
            connectDragSource,
            connectDragPreview,
            connectDropTarget,
            isDraggable,
            isDragging,
            isOver,
            children,
            replaceComponent,
            filter,
            replaceNodeOptions,
            filterText,
            emptyMessageId
        } = this.props;

        const node = replaceNodeOptions?.(nodeProp, 'group') || nodeProp;

        const CustomComponent = replaceComponent(this.props);

        if (CustomComponent) {
            return <CustomComponent { ...this.props } />;
        }

        if (node?.showComponent && !node?.hide && filter(node, 'group')) {
            const draggable = isDraggable;
            const expanded = node.expanded !== undefined ? node.expanded : true;
            const { title, tooltipText } = getTitleAndTooltip({ node, currentLocale });
            const placeholderClassName = (isDragging || node.placeholder ? ' is-placeholder ' : '');
            const selected = selectedNodes.find((s) => s === node.id) ? true : false;
            const isEmpty = node?.nodes?.length === 0;
            const emptyClassName = isEmpty ? ' ms-empty-group' : '';
            const errorClassName = node.loadingError ? ' ms-group-error' : '';
            const selectedClassName = selected ? ' ms-selected' : '';
            const draggableClassName = draggable && ' ms-draggable' || '';
            const draggingClassName = isDragging && ' ms-dragging' || '';
            const overClassName = isOver && ' ms-over' || '';

            const groupHead = (
                <div
                    className="toc-default-group-head"
                    onClick={(event) =>
                        onSelect(node.id, 'group', event.ctrlKey)}>
                    <SideCard
                        size="sm"
                        preview={<Toolbar
                            btnDefaultProps={{
                                className: 'square-button-md'
                            }}
                            buttons={[{
                                visible: !isEmpty,
                                glyph: expanded ? 'collapse-down' : 'expand',
                                onClick: (event) => {
                                    event.stopPropagation();
                                    onToggle(node.id, expanded);
                                }
                            }]}
                        />}
                        className={`ms-toc-group${draggableClassName}${draggingClassName}${overClassName}${selectedClassName}`}
                        title={titleTooltip ? <span data-tip={tooltipText} >{title}</span> : title}
                        tools={<Toolbar
                            btnDefaultProps={{
                                className: 'square-button-md'
                            }}
                            buttons={[{
                                visible: !isEmpty,
                                glyph: node.visibility ? 'eye-open' : 'eye-close',
                                onClick: (event) => {
                                    event.stopPropagation();
                                    propertiesChangeHandler(node.id, { visibility: !node.visibility });
                                }
                            }]}
                        />}
                    />
                </div>
            );

            const groupChildren = children && (
                <GroupChildren
                    node={node}
                    level={level + 1}
                    onSort={onSort}
                    onError={onError}
                    setDndState={setDndState}
                    position="collapsible"
                    filter={filter}>
                    {cloneElement(children, {
                        filterText,
                        emptyMessageId,
                        replaceNodeOptions,
                        filter
                    })}
                </GroupChildren>
            );

            return (
                <>
                <Node
                    node={node}
                    className={`toc-default-group toc-group-${level}${placeholderClassName}${errorClassName}${emptyClassName}`}
                    style={style}
                    animateCollapse={false}
                    type="group">
                    {connectDragPreview(connectDropTarget(draggable ? connectDragSource(groupHead) : groupHead))}
                    {isDragging || node.placeholder ? null : groupChildren}
                    {isEmpty && <div className="ms-nodes-empty">
                        <Message msgId={emptyMessageId || 'noLayerInGroup'}/>
                    </div>}
                </Node>
                {inView && <Portal>
                    <ReactTooltip place="top" type="dark" effect="solid"/>
                </Portal>}
                </>
            );
        }
        return null;
    }

    render() {
        return (
            <InView>
                {({ inView, ref }) => (
                    <div ref={ref}>
                        {this.renderNode(inView)}
                    </div>
                )}
            </InView>
        );
    }
}

export default draggableComponent('LayerOrGroup', memo(GroupNode));
