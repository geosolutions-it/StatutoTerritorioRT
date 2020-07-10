/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import isNaN from 'lodash/isNaN';

import {
    ENABLE_CATALOG_SERAPIDE,
    SELECT_CATALOG_ENTRY_SERAPIDE,
    LOADING_DATA_SERAPIDE,
    UPDATE_CATALOG_RESULTS_SERAPIDE,
    ERROR_CATALOG_RESULTS_SERAPIDE
} from '@js/actions/serapide';

const serapide = (state = {}, action) => {
    switch (action.type) {
    case ENABLE_CATALOG_SERAPIDE: {
        return { ...state, enabled: action.enabled };
    }
    case SELECT_CATALOG_ENTRY_SERAPIDE: {
        return { ...state, selected: action.selected };
    }
    case LOADING_DATA_SERAPIDE: {
        return { ...state, loading: action.loading };
    }
    case UPDATE_CATALOG_RESULTS_SERAPIDE: {
        const { results, totalCount, page } = action.response;
        const numberPage = parseFloat(page);
        return {
            ...state,
            error: false,
            results,
            totalCount,
            page: !isNaN(numberPage)
                ? numberPage
                : undefined
        };
    }
    case ERROR_CATALOG_RESULTS_SERAPIDE: {
        return {
            ...state,
            error: action.error
        };
    }
    default:
        return state;
    }
};

export default serapide;
