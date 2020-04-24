const path = require("path");

const themeEntries = require('./MapStore2/build/themes.js').themeEntries;
const extractThemesPlugin = require('./MapStore2/build/themes.js').extractThemesPlugin;
const USE_REMOTE = process.env.USE_REMOTE || false;
const DEV_SERVER_HOST = process.env.REMOTE_HOST || 'localhost:8000';
const protocol = process.env.REMOTE_PROTOCOL || 'http';
const devServer = USE_REMOTE ? {
    clientLogLevel: 'debug',
    https: protocol === 'https' ? true : false,
    headers: {
        'Access-Control-Allow-Origin': '*'
    }, 
    contentBase: path.join(__dirname),
    before: function (app) {
        app.use(function (req, res, next) {
            if (req.url.indexOf('/static/mapstore/MapStore2/') !== -1) {
                req.url = req.url.replace('/static/mapstore/MapStore2/', '/MapStore2/');
                req.path = req.path.replace('/static/mapstore/MapStore2/', '/MapStore2/');
                req.originalUrl = req.originalUrl.replace('/static/mapstore/MapStore2/', '/MapStore2/');
            }else if (req.url.indexOf('/static/mapstore/translations/') !== -1) {
                req.url = req.url.replace('/static/mapstore/translations/', '/MapStore2/web/client/translations/');
                req.path = req.path.replace('/static/mapstore/translations/', '/MapStore2/web/client/translations/');
                req.originalUrl = req.originalUrl.replace('/static/mapstore/translations/', '/MapStore2/web/client/translations/');
            }
            next();
        });
    },
    proxy: [   
        {
            logLevel: 'debug',
            context: [
                '**',
                '!**/index.html',
                '!**/static/mapstore/**',
                '!**/dist/**',
                '!**/static_config/**',
                '!**/node_modules/**',
                '!**/MapStore2/**',
                '!**/themes/**',
            ],
            target: `${protocol}://${DEV_SERVER_HOST}`,
            headers: {
                Host: DEV_SERVER_HOST,
                Referer: `${protocol}://${DEV_SERVER_HOST}/`
            }
        }
    ]
} : undefined
module.exports = {...require('./MapStore2/build/buildConfig')(
    {
        'Geoportale': path.join(__dirname, "js", "app")
    },
    {'themes/default': themeEntries['themes/default']},
    {
        base: __dirname,
        dist: path.join(__dirname, "dist", "mapstore"),
        framework: path.join(__dirname, "MapStore2", "web", "client"),
        code: [path.join(__dirname, "js"), path.join(__dirname, "MapStore2", "web", "client")]
    },
    extractThemesPlugin,
    false,
    "/static/mapstore/",
    '.Geoportale',
    [],
    {
        "@mapstore": path.resolve(__dirname, "MapStore2", "web", "client"),
        "@js": path.resolve(__dirname, "js")
    }
), devServer
};
