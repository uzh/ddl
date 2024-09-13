const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

const pages = {
    'vue_gpt_uploader': {
        entry: './GPTUploaderApp/src/uploader.js',
        chunks: ['chunk-vendors']
    },
}

module.exports = {
    pages: pages,
    filenameHashing: false,
    runtimeCompiler: true,
    publicPath: '/static/gpt/vue/',
    outputDir: path.resolve('../gpt/static/gpt/vue'),

    devServer: {
        hot: false,
        devMiddleware: {
            writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
        }
    },

    chainWebpack: config => {

        config.optimization
            .splitChunks({
                cacheGroups: {
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: 'chunk-vendors',
                        chunks: 'all',
                        priority: 1
                    },
                },
            });

        Object.keys(pages).forEach(page => {
            config.plugins.delete(`html-${page}`);
            config.plugins.delete(`preload-${page}`);
            config.plugins.delete(`prefetch-${page}`);
        })

        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{
                filename: 'webpack-stats.json',
                path: '../gpt/static/gpt/vue',
                relativePath: true
            }]);

        config.resolve.alias
            .set('__STATIC__', 'static');

        config.module
            .rule('i18n')
            .resourceQuery(/blockType=i18n/)
            .type('javascript/auto')
            .use('i18n')
                .loader('@intlify/vue-i18n-loader')
                .end();
    },

    pluginOptions: {
      i18n: {
        locale: 'en',
        fallbackLocale: 'en',
        localeDir: 'locales',
        enableLegacy: true,
        runtimeOnly: false,
        compositionOnly: true,
        fullInstall: true
      }
    }
};
