'use strict'

const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const BundleTracker = require('webpack-bundle-tracker')

module.exports = {
    mode: "development",

    entry: {
        equipment: './vue_frontend/equipment.js'
    },

    output: {
        filename: "[name].bundle.js",
        path: path.resolve(__dirname, 'static/javascripts')
    },

    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: "vue-loader"
            }

        ]
    },

    plugins: [
        new VueLoaderPlugin(),
        new BundleTracker({filename: './webpack-stats.json'})
    ]
}