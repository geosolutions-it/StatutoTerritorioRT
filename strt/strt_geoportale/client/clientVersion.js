/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the ISC-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* eslint-disable */

const path = require('path');
const fs = require('fs-extra');
const version = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
const versionFileDestination = path.join(__dirname, 'static', 'mapstore', 'version.txt');

fs.writeFile(versionFileDestination,
    'Geoportale_v_' + version,
    function(err) {
        if (err) {
            return console.log(err);
        }
        return console.log(`- version file written ${versionFileDestination}`);
    }
);
