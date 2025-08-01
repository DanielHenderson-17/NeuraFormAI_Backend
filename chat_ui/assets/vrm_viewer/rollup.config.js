const resolve = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");

module.exports = {
  input: "app.js",
  output: {
    file: "bundle.js",
    format: "iife",
    name: "vrmViewer",
    sourcemap: true,
  },
  plugins: [resolve(), commonjs()],
};
