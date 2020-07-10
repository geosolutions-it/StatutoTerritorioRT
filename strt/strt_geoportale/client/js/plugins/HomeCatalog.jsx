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

import Catalog from '@js/plugins/serapidecatalog/Catalog';

import epics from '@js/epics/serapide';
import serapide from '@js/reducers/serapide';

import { searchSerapide } from '@js/actions/serapide';
import { mapTypeSelector } from '@mapstore/selectors/maptype';

import { getMapUrl } from '@js/utils/GeoportaleUtils';

function selectMapSerapideThunk(params) {
    return (dispatch, getState) => {
        const mapType = mapTypeSelector(getState());
        const mapUrl = getMapUrl(mapType, params);
        return dispatch(push(mapUrl));
    };
}

function HomeCatalog(props) {
    return (
        <Grid>
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
    state => state?.serapide?.error
], (selected, loading, results, totalCount, page, error) => ({
    selected,
    loading,
    results,
    totalCount,
    page,
    error
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
