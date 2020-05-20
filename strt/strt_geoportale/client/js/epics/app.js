/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Observable } from 'rxjs';
import { ADD_LAYER, updateNode } from '@mapstore/actions/layers';
import find from 'lodash/find';
import { groupsSelector } from '@mapstore/selectors/layers';

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
            const DEFAULT_GROUP_ID = 'Default';
            const defaultGroup = find(groups, ({ id }) => id === DEFAULT_GROUP_ID);
            if (defaultGroup && defaultGroup.title !== title) {
                return Observable.of(updateNode(DEFAULT_GROUP_ID, 'groups', { title }));
            }
            return Observable.empty();
        });

export default {
    strtUpdateDefaultGroup
};
