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

Read more on the [wiki](undefined/wiki).

## Update the static map list (development only)

The static maps available in the geoportale homepage are listed in this customizable file [defaultMaps.json](static/mapstore/defaultMaps.json).

The defaults available maps are:

- [mappa_piani_operativi.json](static/mapstore/mappa_piani_operativi.json)
- [mappa_piani_strutturali.json](static/mapstore/mappa_piani_strutturali.json)

Due to the size of this json we introduced this file ([staticMapsUtils.js](js/staticMapsUtils.js)) to help the composition of this maps and retrieve additional information of the layers via WMS Get Capabilities.

The staticMapsUtils.js provides the json results via console.log and it have only a development purpose. These are the needed steps to work with the staticMapsUtils.js file:

- Install packages: `npm install`
- Start the client: `npm start`
- Temporarily uncomment the import('../staticMapsUtils.js') in [serapide.js](js/epics/serapide.js) epics file
- Change the code and use the available functions to print the layers and maps json text in the dev tool
- Copy the log results to the related static file
- Comment again the import('../staticMapsUtils.js') in [serapide.js](js/epics/serapide.js) epics file before commit the changes on the static files

Available functions:

- printLayersOfPianiOperativi -> copy result to -> [layers/piani_operativi.json](static/mapstore/layers/piani_operativi.json)
- printLayersOfPianiStutturali -> copy result to -> [layers/piani_strutturali.json](static/mapstore/layers/piani_strutturali.json)
- printLayersOfInvarianti -> copy result to -> [layers/invarianti.json](static/mapstore/layers/invarianti.json)
- printLayersOfPianoPaesaggisticoRegionale -> copy result to -> [layers/piano_paesaggistico_regionale.json](static/mapstore/layers/piano_paesaggistico_regionale.json)
- printLayersOfCartografiaDiBase -> copy result to -> [layers/cartografia_di_base.json](static/mapstore/layers/cartografia_di_base.json)
- printLayersOfRisorse -> copy result to -> [layers/risorse.json](static/mapstore/layers/risorse.json)

- printStaticMaps -> copy result to -> 
    - [mappa_piani_operativi.json](static/mapstore/mappa_piani_operativi.json)
    - [mappa_piani_strutturali.json](static/mapstore/mappa_piani_strutturali.json)

The above function could run capabilities request to get information about layers so dispatch them only if needed.