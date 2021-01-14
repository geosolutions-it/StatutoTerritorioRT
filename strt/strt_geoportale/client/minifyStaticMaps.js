/**
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the ISC-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* eslint-disable */

const path = require('path');
const fs = require('fs');
const staticDirectory = path.join(__dirname, 'static', 'mapstore');
const mapsDirectory = path.join(__dirname, 'static', 'mapstore', 'maps');
const files = fs.readdirSync(mapsDirectory);

files.forEach(file => {
    const minMap = JSON.stringify(JSON.parse(fs.readFileSync(path.resolve(mapsDirectory, file))));
    fs.writeFile(
        path.resolve(staticDirectory, file),
        minMap,
        function(err) {
            if (err) {
                return console.log(err);
            }
            return console.log(`SUCCESS ${file}`);
        }
    );
});
