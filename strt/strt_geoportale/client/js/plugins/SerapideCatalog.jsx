/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React from 'react';
import { connect } from 'react-redux';
import { createSelector } from 'reselect';
import { createPlugin } from '@mapstore/utils/PluginsUtils';
import PropTypes from 'prop-types';
import ResizableModal from '@mapstore/components/misc/ResizableModal';
import Portal from '@mapstore/components/misc/Portal';
import Message from '@mapstore/components/I18N/Message';

import Catalog from '@js/plugins/serapidecatalog/Catalog';
import {
    enableCatalogSerapide,
    searchSerapide,
    selectCatalogEntrySerapide
} from '@js/actions/serapide';

import epics from '@js/epics/serapide';
import serapide from '@js/reducers/serapide';

function SerapideCatalogPlugin({ enabled, onClose, ...props }) {
    return (
        <Portal>
            <ResizableModal
                show={enabled}
                title={<Message msgId="serapide.catalogTitle"/>}
                size="lg"
                onClose={onClose}>
                <Catalog {...props} />
            </ResizableModal>
        </Portal>
    );
}

SerapideCatalogPlugin.propTypes = {
    enabled: PropTypes.boolean,
    onClose: PropTypes.func
};

SerapideCatalogPlugin.defaultProps = {
    onClose: () => {}
};

const selector = createSelector([
    state => state?.serapide?.enabled || false,
    state => state?.serapide?.selected,
    state => state?.serapide?.loading,
    state => state?.serapide?.results,
    state => state?.serapide?.totalCount,
    state => state?.serapide?.page,
    state => state?.serapide?.error
], (enabled, selected, loading, results, totalCount, page, error) => ({
    enabled,
    selected,
    loading,
    results,
    totalCount,
    page,
    error
}));

function TOCButton({
    onClick
}) {
    return (
        <a onClick={() => onClick()}>
            <Message msgId="serapide.selectSerapideLayers"/>
        </a>
    );
}

export default createPlugin('SerapideCatalog', {
    component: connect(selector, {
        onSelect: selectCatalogEntrySerapide,
        onClose: enableCatalogSerapide.bind(null, false),
        onSearch: searchSerapide
    })(SerapideCatalogPlugin),
    containers: {
        TOC: {
            name: 'serapidecatalog',
            serapideButton: connect(() => ({}), {
                onClick: enableCatalogSerapide.bind(null, true)
            })(TOCButton)
        }
    },
    reducers: {
        serapide
    },
    epics
});
