const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  entry: {
    'layout/layout': './app/static/src/js/new_layout.js',
    'landing_page': './app/static/src/js/landing_page.js',
    'entrepreneur/company_list': './app/static/src/js/entrepreneur/company_list.js',
    'entrepreneur/job_offers_list': './app/static/src/js/entrepreneur/job_offers_list.js'
  },
  output: {
    filename: 'js/[name].min.js',
    path: path.resolve(__dirname, './app/static/public/')
  },
  plugins: [
    new CleanWebpackPlugin(['./app/static/public/']),
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      Bloodhound: 'typeahead.js/dist/bloodhound.min.js'
    })
  ]
}
