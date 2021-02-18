Geoportale Regione Toscana
==========

Quick Start
------------

Clone the repository with the --recursive option to automatically clone submodules:

`git clone --recursive undefined`

Install NodeJS >= 7.10.0 , if needed, from [here](https://nodejs.org/en/download/releases/).

Start the development application locally:

`npm install`

`npm start`

The application runs at `http://localhost:8081` afterwards.

## Update static maps

The static maps available in the geoportale homepage are listed in this customizable file [defaultMaps.json](static/mapstore/defaultMaps.json).

The defaults available maps are:

- [mappa_piani_operativi.json](static/mapstore/mappa_piani_operativi.json)
- [mappa_piani_strutturali.json](static/mapstore/mappa_piani_strutturali.json)

It is possible update static maps running the following steps:

- edit the json files with needed changes
- (optional) synch some properties with capabilities with the command `npm run update-static-maps`
- minify the maps with the command `npm run minify-static-maps`

Note: the `npm run update-static-maps` command use the [updateMapConfig.js](updateMapConfig.js) and currently updates only min/max scales and resolutions. The `updateLayer` function can be enhanced in case of additional updates.