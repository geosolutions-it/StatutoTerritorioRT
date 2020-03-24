/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

export const globalAuth = {
    _attore_attivo: "",
    _ruolo: ""
}
export const setAuthProperty = (property = "", value ="") => {
  globalAuth[property] = value;
}


// TODO: remove after migration to new model the permission to execute an action comes with action its self from the backend
export const canExecuteAction = () => false;