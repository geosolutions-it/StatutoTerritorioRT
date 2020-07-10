/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

export const ENABLE_CATALOG_SERAPIDE = 'ENABLE_CATALOG:SERAPIDE';
export const SELECT_CATALOG_ENTRY_SERAPIDE = 'SELECT_CATALOG_ENTRY:SERAPIDE';
export const UPDATE_CATALOG_RESULTS_SERAPIDE = 'UPDATE_CATALOG_RESULTS:SERAPIDE';
export const ERROR_CATALOG_RESULTS_SERAPIDE = 'ERROR_CATALOG_RESULTS_SERAPIDE';
export const LOADING_DATA_SERAPIDE = 'LOADING_DATA:SERAPIDE';
export const SEARCH_SERAPIDE = 'SEARCH:SERAPIDE';

export const enableCatalogSerapide = (enabled) => ({
    type: ENABLE_CATALOG_SERAPIDE,
    enabled
});

export const selectCatalogEntrySerapide = (selected) => ({
    type: SELECT_CATALOG_ENTRY_SERAPIDE,
    selected
});

export const updateCatalogResultsSerapide = (response) => ({
    type: UPDATE_CATALOG_RESULTS_SERAPIDE,
    response
});

export const errorCatalogResultsSerapide = (error) => ({
    type: ERROR_CATALOG_RESULTS_SERAPIDE,
    error
});

export const loadingDataSerapide = (loading) => ({
    type: LOADING_DATA_SERAPIDE,
    loading
});

export const searchSerapide = (params) => ({
    type: SEARCH_SERAPIDE,
    params
});
