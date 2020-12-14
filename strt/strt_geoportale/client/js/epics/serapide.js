/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Observable } from 'rxjs';
import { layersSelector } from '@mapstore/selectors/layers';
import {
    addLayer,
    addGroup,
    removeLayer,
    moveNode,
    updateNode
} from '@mapstore/actions/layers';
import { setControlProperty } from '@mapstore/actions/controls';
import { zoomToExtent } from '@mapstore/actions/map';
import { MAP_CONFIG_LOADED } from '@mapstore/actions/config';
import {
    SELECT_CATALOG_ENTRY_SERAPIDE,
    selectCatalogEntrySerapide,
    SEARCH_SERAPIDE,
    updateCatalogResultsSerapide,
    errorCatalogResultsSerapide,
    loadingDataSerapide,
    setDefaultMaps,
    setEmptyCatalog
} from '@js/actions/serapide';

import {
    requestSerapideDataById,
    requestSerapideData,
    getSerapideGroups
} from '@js/api';

import {
    push,
    replace
} from 'connected-react-router';
import {
    getMapUrl,
    ID_PARAM,
    get4326BBOX,
    mergeLayersBBOXs,
    setDefaultGroupsIds,
    getDefaultGroupsIds
} from '@js/utils/GeoportaleUtils';

import { error as errorNotification } from '@mapstore/actions/notifications';

import capitalize from 'lodash/capitalize';

import url from 'url';
import uuidv1 from 'uuid/v1';
import { LOCATION_CHANGE } from 'connected-react-router';
import axios from '@mapstore/libs/ajax';

export const strtInitApp = action$ =>
    action$.ofType(LOCATION_CHANGE)
        .switchMap((action) => {
            if (action?.payload?.isFirstRendering) {
                return Observable.defer(() =>
                    axios.get('/static/mapstore/defaultMaps.json')
                        .then(({ data }) => data.results)
                        .catch(() => [])
                )
                    .switchMap((results) => {
                        return Observable.of(setDefaultMaps(results)); 
                    });
            }
            return Observable.empty();
        })
        .take(1);

export const strtAddMapConfigurations = (action$, store) =>
    action$.ofType(MAP_CONFIG_LOADED)
        .switchMap(() =>{
            return Observable.defer(() => getSerapideGroups())
                .switchMap((defaultGroups) => {
                    const state = store.getState();
                    const search = state?.router?.location?.search;
                    const { query = {} } = search && url.parse(search, true) || {};
                    if (query.static) {
                        return Observable.of(
                            setControlProperty('drawer', 'enabled', true)
                        );
                    }
                    const id = query[ID_PARAM];
                    setDefaultGroupsIds(defaultGroups.map((group) => group.id));
                    const addGroupsActions = defaultGroups.map(({ parent, ...group }) =>
                        addGroup(undefined, parent, group)
                    );
                    if (!id) {
                        return Observable.of(
                            ...addGroupsActions,
                            // move piano group on top of TOC
                            moveNode('piano', 'root', 0),
                            setControlProperty('drawer', 'enabled', true)
                        );
                    }
                    return Observable.of(
                        ...addGroupsActions,
                        // move piano group on top of TOC
                        moveNode('piano', 'root', 0),
                        selectCatalogEntrySerapide({ id }),
                        setControlProperty('drawer', 'enabled', true)
                    );
                });
        });

export const strtSearchSerapide = (action$) =>
    action$.ofType(SEARCH_SERAPIDE)
        .switchMap((action) => {
            const { params, isFirstRequest } = action;
            return Observable.defer(() => requestSerapideData(params))
                .switchMap((response) => {
                    const { results = [], totalCount, page } = response || {};
                    const isCatalogEmpty = !!(totalCount === 0 && results.length === 0 && !params.q);
                    return Observable.of(
                        ...(isFirstRequest ? [ setEmptyCatalog(isCatalogEmpty) ] : []),
                        updateCatalogResultsSerapide({ results, totalCount, page }),
                        loadingDataSerapide(false)
                    );
                })
                .catch((error) => {
                    return Observable.of(
                        loadingDataSerapide(false),
                        errorCatalogResultsSerapide(error?.message || true)
                    );
                })
                .startWith(loadingDataSerapide(true), errorCatalogResultsSerapide(false));
        });

export const strtSelectCatalogEntrySerapide = (action$, store) =>
    action$.ofType(SELECT_CATALOG_ENTRY_SERAPIDE)
        .switchMap((action) =>{
            const state = store.getState();
            const { selected } = action;
            const mapId = state?.mapInitialConfig?.mapId;

            if (selected.mapId !== undefined && selected.mapId !== mapId) {
                const mapUrl = getMapUrl(selected);
                return Observable.of(push(mapUrl));
            }

            const search = state?.router?.location?.search;
            const { query = {} } = search && url.parse(search, true) || {};
            const newSearch = url.format({
                query: {
                    ...query,
                    [ID_PARAM]: selected.id
                }
            });

            return Observable.concat(
                Observable.of(replace({ search: newSearch })),
                Observable.defer(() => requestSerapideDataById(selected.id))
                    .switchMap((response) => {
                        const {
                            map,
                            comune,
                            name,
                            type
                        } = response || {};
                        const configLayers = map?.layers;
                        if (!configLayers) {
                            return Observable.of(loadingDataSerapide(false));
                        }

                        const currentLayers = layersSelector(store.getState());
                        const defaultGroupsId = getDefaultGroupsIds();

                        const removeLayersActions = currentLayers
                            .filter(({group}) => defaultGroupsId.indexOf(group) !== -1)
                            .map(({ id }) => removeLayer(id));

                        const newLayers = configLayers
                            .map(layer => ({
                                visibility: true,
                                singleTile: false,
                                ...layer,
                                group: layer?.group
                                    ? 'piano.' + layer.group
                                    : undefined,
                                bbox: get4326BBOX(layer.bbox),
                                id: uuidv1()
                            }));

                        const bbox = mergeLayersBBOXs(newLayers);

                        const addLayersActions = newLayers
                            .map(layer => addLayer(layer));

                        return Observable.of(
                            ...(bbox
                                ? [ zoomToExtent(bbox.bounds, bbox.crs) ]
                                : []),
                            ...removeLayersActions,
                            ...addLayersActions,
                            updateNode('piano', 'groups', {
                                title: 'Piano ' + capitalize(type),
                                description: 'nome: ' + name,
                                caption: 'comune: ' + comune
                            }),
                            loadingDataSerapide(false)
                        );
                    })
                    .catch(({ data }) => {
                        const errorMessage = data?.err;
                        return Observable.of(
                            errorNotification({
                                title: 'serapide.noPianoAvailableTitle',
                                message: errorMessage
                                    ? 'serapide.genericError'
                                    : 'serapide.noPianoAvailable',
                                values: {
                                    errorMessage
                                }
                            }),
                            loadingDataSerapide(false)
                        );
                    })
                    .startWith(loadingDataSerapide(true))
            );
        });

export default {
    strtAddMapConfigurations,
    strtSearchSerapide,
    strtSelectCatalogEntrySerapide,
    strtInitApp
};
