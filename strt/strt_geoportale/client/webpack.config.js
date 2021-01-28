const path = require('path');

const extractThemesPlugin = require('./MapStore2/build/themes.js').extractThemesPlugin;
const PORT = '8082';
const USE_REMOTE = process.env.USE_REMOTE || true;
const DEV_SERVER_HOST = process.env.REMOTE_HOST || 'localhost:8000';
const protocol = process.env.REMOTE_PROTOCOL || 'http';

const devServer = USE_REMOTE ? {
    clientLogLevel: 'debug',
    https: protocol === 'https' ? true : false,
    headers: {
        'Access-Control-Allow-Origin': '*'
    },
    port: PORT,
    contentBase: path.join(__dirname),
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
                '!**/static/config.json',
                '!**/translations/**'
            ],
            target: `${protocol}://${DEV_SERVER_HOST}`,
            headers: {
                Host: DEV_SERVER_HOST,
                Referer: `${protocol}://${DEV_SERVER_HOST}/`
            }
        },
        {
            context: [
                '/static/mapstore/translations/**',
                '/static/mapstore/MapStore2/**',
                '/static/mapstore/MapStore2/web/client/translations/**'
            ],
            target: `${protocol}://localhost:${PORT}`,
            secure: false,
            changeOrigin: true,
            pathRewrite: {
                '/static/mapstore/translations/': '/translations/',
                '/static/mapstore/MapStore2/web/client/translations/': '/MapStore2/web/client/translations/',
                '/static/mapstore/MapStore2/': '/MapStore2/'
            }
        }
    ]
} : undefined;

module.exports = {...require('./MapStore2/build/buildConfig')(
    {
        'Geoportale': path.join(__dirname, 'js', 'app')
    },
    {'themes/default': path.join(__dirname, 'themes', 'default', 'theme.less')},
    {
        base: __dirname,
        dist: path.join(__dirname, 'dist', 'mapstore'),
        framework: path.join(__dirname, 'MapStore2', 'web', 'client'),
        code: [path.join(__dirname, 'js'), path.join(__dirname, 'MapStore2', 'web', 'client')]
    },
    extractThemesPlugin,
    false,
    '/static/mapstore/',
    '.Geoportale',
    [],
    {
        '@mapstore': path.resolve(__dirname, 'MapStore2', 'web', 'client'),
        '@js': path.resolve(__dirname, 'js')
    }
), devServer
};
