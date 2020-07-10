/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import axios from '@mapstore/libs/ajax';
import { getConfigProp } from '@mapstore/utils/ConfigUtils';

const DEFAULT_ENDPOINTS = {
    geoMapSearch: '/serapide/geo/map/search',
    geoMapId: '/serapide/geo/map/{id}',
    geoGroups: '/serapide/geo/groups'
};

export const requestSerapideData = (params) => {
    const { geoMapSearch } = getConfigProp('serapideAPI') || DEFAULT_ENDPOINTS;
    return axios.get(geoMapSearch, { params })
        .then(({ data }) => data);
};

export const requestSerapideDataById = (id) => {
    const { geoMapId } = getConfigProp('serapideAPI') || DEFAULT_ENDPOINTS;
    return axios.get(geoMapId.replace(/\{id\}/g, id))
        .then(({ data }) => data);
};

export const getSerapideGroups = () => {
    const { geoGroups } = getConfigProp('serapideAPI') || DEFAULT_ENDPOINTS;
    return axios.get(geoGroups)
        .then(({ data }) => {
            const { groups = [] } = data || [];
            const newGroups = groups.map(({ id, title }) => ({
                id: 'piano.' + id,
                title,
                expanded: true,
                parent: 'piano'
            }));
            return [
                {
                    id: 'piano',
                    title: 'Piano',
                    expanded: true
                },
                ...newGroups
            ];
        })
        .catch(() => []);
};

