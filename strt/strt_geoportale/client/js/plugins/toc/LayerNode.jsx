/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { Component, memo } from 'react';
import PropTypes from 'prop-types';
import Node from '@mapstore/components/TOC/Node';
import { getTitleAndTooltip } from '@mapstore/utils/TOCUtils';
import castArray from 'lodash/castArray';
import find from 'lodash/find';
import { Glyphicon} from 'react-bootstrap';
import draggableComponent from '@mapstore/components/TOC/enhancers/draggableComponent';
import WMSLegend from '@mapstore/components/TOC/fragments/WMSLegend';
import OpacitySlider from '@mapstore/components/TOC/fragments/OpacitySlider';
import SideCard from '@mapstore/components/misc/cardgrids/SideCard';
import Toolbar from '@mapstore/components/misc/toolbar/Toolbar';
import Highlighter from 'react-highlight-words';
import ReactTooltip from 'react-tooltip';
import Portal from '@mapstore/components/misc/Portal';
import tooltip from '@mapstore/components/misc/enhancers/tooltip';
import { InView } from 'react-intersection-observer';

const GlyphIndicator = tooltip(Glyphicon);

const layerToolsByTypes = {
    wms: {
        isActive: ({ activateLegendTool }) => activateLegendTool,
        Tools: ({ node, currentZoomLvl, scales, legendOptions }) => {
            return (
                <>
                <WMSLegend
                    node={node}
                    currentZoomLvl={currentZoomLvl}
                    scales={scales}
                    { ...legendOptions }
                />
                </>
            );
        }
    },
    link: {
        isActive: () => false
    }
};

export class LayerNode extends Component {

    static propTypes = {
        node: PropTypes.object,
        onSelect: PropTypes.func,
        style: PropTypes.object,
        activateLegendTool: PropTypes.bool,
        activateOpacityTool: PropTypes.bool,
        indicators: PropTypes.array,
        currentZoomLvl: PropTypes.number,
        scales: PropTypes.array,
        legendOptions: PropTypes.object,
        currentLocale: PropTypes.string,
        selectedNodes: PropTypes.array,
        filterText: PropTypes.string,
        onUpdateNode: PropTypes.func,
        titleTooltip: PropTypes.bool,
        filter: PropTypes.func,
        hideOpacityTooltip: PropTypes.bool,
        tooltipOptions: PropTypes.object,
        connectDragPreview: PropTypes.func,
        connectDragSource: PropTypes.func,
        connectDropTarget: PropTypes.func,
        isDraggable: PropTypes.bool,
        isDragging: PropTypes.bool,
        replaceNodeOptions: PropTypes.func,
        onRemove: PropTypes.func,
        enableInlineRemove: PropTypes.func
    };

    static defaultProps = {
        style: {},
        onSelect: () => {},
        activateLegendTool: false,
        activateOpacityTool: true,
        indicators: [],
        currentLocale: 'en-US',
        selectedNodes: [],
        filterText: '',
        onUpdateNode: () => {},
        filter: () => true,
        titleTooltip: false,
        hideOpacityTooltip: false,
        connectDragPreview: (cmp) => cmp,
        connectDragSource: (cmp) => cmp,
        connectDropTarget: (cmp) => cmp,
        onRemove: () => {},
        enableInlineRemove: () => true
    };

    renderNode(inView) {

        const {
            node: nodeProp,
            filter,
            isDraggable,
            filterText,
            currentLocale,
            connectDropTarget,
            connectDragSource,
            isDragging,
            connectDragPreview,
            style,
            selectedNodes,
            onUpdateNode,
            onSelect,
            activateOpacityTool,
            hideOpacityTooltip,
            replaceNodeOptions,
            titleTooltip,
            indicators,
            onRemove,
            enableInlineRemove
        } = this.props;

        const node = replaceNodeOptions?.(nodeProp, 'layer') || nodeProp;

        const { title, tooltipText: titleTooltipText } = getTitleAndTooltip({ node, currentLocale });
        const tooltipText = node?.description || titleTooltipText;
        const isDummy = !!node?.dummy;
        const expanded = node.expanded;

        const placeholderClassName = (isDragging || node.placeholder ? ' is-placeholder ' : '');

        const hideClassName = node.type !== 'link' && (!node.visibility || node.invalid) ? ' ms-hide' : '';
        const selectedClassName = selectedNodes.find((nodeId) => nodeId === node.id) ? ' ms-selected' : '';
        const errorClassName = node.loadingError === 'Error' ? ' ms-node-error' : '';
        const warningClassName = node.loadingError === 'Warning' ? ' ms-node-warning' : '';

        const { Tools = null, isActive = () => true } = layerToolsByTypes[node.type] || {};

        const Body = isActive(this.props) && Tools;

        /** initial support to render icons in TOC nodes (now only type = "dimension" supported) */
        const indicatorsComponents = castArray(indicators)
            .map(indicator =>
                (indicator.type === 'dimension' ? find(node?.dimensions || [], indicator.condition) : false)
                    ? indicator.glyph && ({
                        Element: () => <GlyphIndicator
                            key={indicator.key}
                            glyph={indicator.glyph}
                            {...indicator.props}
                        />
                    })
                    : null);

        const titleComponent = filterText
            ? <Highlighter
                searchWords={[ filterText ]}
                autoEscape
                textToHighlight={title}
            />
            : title;

        const head = (
            <div
                onClick={(event) =>
                    node.type !== 'link' && onSelect(node.id, 'layer', event.ctrlKey)}>
                <SideCard
                    size="sm"
                    style={{
                        cursor: 'pointer'
                    }}
                    preview={<Toolbar
                        btnDefaultProps={{
                            className: 'square-button-md'
                        }}
                        buttons={[{
                            glyph: expanded ? 'collapse-down' : 'expand',
                            tooltipId: inView ? 'toc.displayLegendAndTools' : undefined,
                            visible: !!Body,
                            onClick: (event) => {
                                event.stopPropagation();
                                onUpdateNode(node.id, 'layers', { expanded: !expanded });
                            }
                        },
                        {
                            visible: node.type === 'link',
                            Element: () => <GlyphIndicator glyph="link" style={{ padding: '0 4px' }}/>
                        }]}
                    />}
                    className={`ms-toc-layer${selectedClassName}${errorClassName}${warningClassName}`}
                    title={titleTooltip ? <span data-tip={tooltipText} data-for={node.id} >{titleComponent}</span> : titleComponent}
                    tools={node.type !== 'link' && <Toolbar
                        btnDefaultProps={{
                            className: 'square-button-md'
                        }}
                        buttons={[
                            ...indicatorsComponents,
                            {
                                visible: !!node?.layerFilter,
                                glyph: 'filter-layer',
                                active: !node?.layerFilter?.disabled,
                                tooltipId: inView
                                    ? node?.layerFilter?.disabled ? 'toc.filterIconDisabled' : 'toc.filterIconEnabled'
                                    : undefined,
                                onClick: (event) => {
                                    event.stopPropagation();
                                    const layerFilter = node?.layerFilter;
                                    onUpdateNode(node.id, 'layer', {layerFilter: { ...layerFilter, disabled: !layerFilter?.disabled }});
                                }
                            },
                            {
                                glyph: 'trash',
                                tooltipId: 'toc.toolTrashLayerTooltip',
                                visible: enableInlineRemove(node),
                                onClick: (event) => {
                                    event.stopPropagation();
                                    onRemove(node.id);
                                }
                            },
                            {
                                visible: !!errorClassName,
                                Element: () => <GlyphIndicator glyph="exclamation-mark" tooltipId="toc.loadingerror"/>
                            },
                            {
                                glyph: node.visibility ? 'eye-open' : 'eye-close',
                                tooltipId: inView
                                    ? warningClassName ? 'toc.toggleLayerVisibilityWarning' : 'toc.toggleLayerVisibility'
                                    : undefined,
                                loading: !!node.loading,
                                onClick: (event) => {
                                    event.stopPropagation();
                                    onUpdateNode(node.id, 'layer', { visibility: !node.visibility });
                                }
                            }
                        ]}
                    />}
                    body={
                        <>
                        {expanded && Body && <div className="ms-layer-node-body"><Body { ...this.props } /></div>}
                        {node.type !== 'link' && activateOpacityTool &&
                            <OpacitySlider
                                opacity={node.opacity}
                                disabled={!node.visibility}
                                hideTooltip={hideOpacityTooltip}
                                onChange={opacity => onUpdateNode(node.id, 'layer', { opacity })}/>
                        }
                        </>
                    }
                />
            </div>
        );

        const tocListItem = (
            <div
                style={isDummy ? { opacity: 0, boxShadow: 'none' } : {}}
                className="toc-list-item">
                {isDummy
                    ? <div style={{ padding: 0, height: 0 }} className="toc-default-layer-head"/>
                    : <Node
                        node={node}
                        className={`toc-default-layer${placeholderClassName}${hideClassName}`}
                        style={style}
                        animateCollapse={false}
                        type="layer">
                        {isDraggable ? connectDragPreview(head) : head}
                    </Node>}
                {inView && <Portal>
                    <ReactTooltip className="toc-layer-tooltip" id={node.id} place="top" type="dark" effect="solid" multiline />
                </Portal>}
            </div>
        );

        const tocListItemNode = node.type === 'link'
            ? <a href={node.href}
                target="_blank"
                rel="noopener noreferrer">
                {tocListItem}
            </a>
            : tocListItem;

        if (node?.showComponent !== false && !node?.hide && filter(node, 'layer')) {
            return connectDropTarget(isDraggable && !isDummy
                ? connectDragSource(tocListItemNode)
                : tocListItemNode);
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

export default draggableComponent('LayerOrGroup', memo(LayerNode));
