const path = require("path");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const themeEntries = require('./MapStore2/build/themes.js').themeEntries;
const extractThemesPlugin = require('./MapStore2/build/themes.js').extractThemesPlugin;
const HtmlWebpackPlugin = require('html-webpack-plugin');

const paths = {
    base: __dirname,
    dist: path.join(__dirname, "dist", "mapstore"),
    framework: path.join(__dirname, "MapStore2", "web", "client"),
    code: [path.join(__dirname, "js"), path.join(__dirname, "MapStore2", "web", "client")]
};

module.exports = require('./MapStore2/build/buildConfig')(
    {
        'Geoportale': path.join(__dirname, "js", "app")
    },
    {'themes/default': themeEntries['themes/default']},
    paths,
    extractThemesPlugin,
    true,
    "/static/mapstore/",
    '.Geoportale',
    [
        new CopyWebpackPlugin([
            { from: path.join(paths.framework, 'translations'), to: path.join(paths.dist, "translations") }
        ]),
    ],
    {
        "@mapstore": path.resolve(__dirname, "MapStore2", "web", "client"),
        "@js": path.resolve(__dirname, "js")
    }
);
