const path = require("path");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const extractThemesPlugin = require('./MapStore2/build/themes.js').extractThemesPlugin;

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
    {'themes/default': path.join(__dirname, "themes", "default", "theme.less")},
    paths,
    extractThemesPlugin,
    true,
    "/static/mapstore/",
    '.Geoportale',
    [
        new CopyWebpackPlugin([
            { from: path.join(paths.framework, 'translations'), to: path.join(paths.dist, "MapStore2", "web", "client", "translations") },
            { from: path.join(paths.base, 'translations'), to: path.join(paths.dist, "translations") }
        ])
    ],
    {
        "@mapstore": path.resolve(__dirname, "MapStore2", "web", "client"),
        "@js": path.resolve(__dirname, "js")
    }
);
