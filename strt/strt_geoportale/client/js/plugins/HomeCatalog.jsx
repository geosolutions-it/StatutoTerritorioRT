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
import { Grid } from 'react-bootstrap';
import { push } from 'connected-react-router';

import StaticCatalog from '@js/plugins/serapidecatalog/StaticCatalog';
import Catalog from '@js/plugins/serapidecatalog/Catalog';

import epics from '@js/epics/serapide';
import serapide from '@js/reducers/serapide';

import { searchSerapide } from '@js/actions/serapide';

import { getMapUrl } from '@js/utils/GeoportaleUtils';

function selectMapSerapideThunk(params) {
    return (dispatch) => {
        const mapUrl = getMapUrl(params);
        return dispatch(push(mapUrl));
    };
}

const ConnectedStaticCatalog = connect(createSelector(
    [
        state => state?.serapide?.defaultMaps
    ], (results) => ({
        results
    }),
), {
    onSelect: selectMapSerapideThunk
})(StaticCatalog);

function HomeCatalog(props) {
    return (
        <Grid className="strt-homepage-catalog" fluid>
            <ConnectedStaticCatalog />
            <Catalog { ...props }/>
        </Grid>
    );
}

const selector = createSelector([
    state => state?.serapide?.selected,
    state => state?.serapide?.loading,
    state => state?.serapide?.results,
    state => state?.serapide?.totalCount,
    state => state?.serapide?.page,
    state => state?.serapide?.error,
    state => state?.serapide?.isCatalogEmpty
], (selected, loading, results, totalCount, page, error, isCatalogEmpty) => ({
    selected,
    loading,
    results,
    totalCount,
    page,
    error,
    isCatalogEmpty
}));

export default createPlugin('HomeCatalog', {
    component: connect(selector, {
        onSelect: selectMapSerapideThunk,
        onSearch: searchSerapide
    })(HomeCatalog),
    reducers: {
        serapide
    },
    epics
});
