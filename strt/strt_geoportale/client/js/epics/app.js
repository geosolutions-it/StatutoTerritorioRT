/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Observable } from 'rxjs';
import { ADD_LAYER, REMOVE_LAYER, updateNode, removeNode } from '@mapstore/actions/layers';
import find from 'lodash/find';
import { groupsSelector, layersSelector } from '@mapstore/selectors/layers';
import url from 'url';
import { LOCATION_CHANGE } from 'connected-react-router';
import { zoomToExtent, CHANGE_MAP_LIMITS } from '@mapstore/actions/map';
import { isValidExtent } from '@mapstore/utils/CoordinatesUtils';

const DEFAULT_GROUP_ID = 'Default';
const LOCAL_SHAPE_GROUP_ID = 'Local shape';
/*
update the default group using the message id 'serapide.userLayers' from translations
*/
export const strtUpdateDefaultGroup = (action$, store) =>
    action$.ofType(ADD_LAYER)
        .switchMap(() =>{
            const state = store.getState();
            const messages = state?.locale?.messages || {};
            const message = messages?.serapide?.userLayers;
            const title = message || 'User Layers';
            const groups = groupsSelector(state);
            const defaultGroup = find(groups, ({ id }) => id === DEFAULT_GROUP_ID);
            if (defaultGroup && defaultGroup.title !== title) {
                return Observable.of(updateNode(DEFAULT_GROUP_ID, 'groups', { title }));
            }
            const localShapeMessage = messages?.serapide?.localShapeLayers;
            const localShapeTitle = localShapeMessage || 'Livelli Importati';
            const localShapeGroup = find(groups, ({ id }) => id === LOCAL_SHAPE_GROUP_ID);
            if (localShapeGroup && localShapeGroup.title !== localShapeTitle) {
                return Observable.of(updateNode(LOCAL_SHAPE_GROUP_ID, 'groups', { title: localShapeTitle }));
            }
            return Observable.empty();
        });

// remove default group if empty
export const strtRemoveDefaultGroup = (action$, store) =>
    action$.ofType(REMOVE_LAYER)
        .switchMap(() =>{
            const state = store.getState();
            const defaultGroupLayers = layersSelector(state).filter(({ group }) => group === undefined || group === DEFAULT_GROUP_ID);
            if (defaultGroupLayers.length === 0) {
                return Observable.of(removeNode(DEFAULT_GROUP_ID, 'groups'));
            }
            return Observable.empty();
        });

// override to ensure the share bbox param zoom to the correct extent
export const strtReadQueryParamsOnMapEpic = (action$, store) =>
    action$.ofType(LOCATION_CHANGE)
        .switchMap(() =>
            action$.ofType(CHANGE_MAP_LIMITS)
                .take(1)
                .switchMap(() => {
                    const state = store.getState();
                    const search = state?.router?.location?.search || '';
                    const { query = {} } = url.parse(search, true) || {};
                    const bbox = query?.bbox || '';
                    const extent = bbox.split(',')
                        .map(val => parseFloat(val))
                        .filter((val, idx) => idx % 2 === 0
                            ? val > -180.5 && val < 180.5
                            : val >= -90 && val <= 90)
                        .filter(val => !isNaN(val));
                    if (extent && extent.length === 4 && isValidExtent(extent)) {
                        return Observable.of(
                            zoomToExtent(extent, 'EPSG:4326', undefined,  {nearest: true})
                        );
                    }
                    return Observable.empty();
                })
        );

export default {
    strtUpdateDefaultGroup,
    strtRemoveDefaultGroup,
    strtReadQueryParamsOnMapEpic
};
