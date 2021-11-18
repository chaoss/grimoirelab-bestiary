var path = require('path');

module.exports = {
  publicPath: "/",
  outputDir: path.resolve(__dirname, "../bestiary/", "core", "static"),
  indexPath: path.resolve(__dirname, "../bestiary", "core", "templates", "index.html"),
  transpileDependencies: ["vuetify"]
};
