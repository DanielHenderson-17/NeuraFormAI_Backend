// rollup.config.test.js - Configuration for bundling test files
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";

export default {
  input: "appTest.js",
  output: {
    file: "bundleTest.js",
    format: "es",
    sourcemap: true,
  },
  plugins: [
    resolve({
      browser: true,
      preferBuiltins: false,
    }),
    commonjs(),
  ],
  external: [],
  onwarn: (warning, warn) => {
    // Suppress certain warnings
    if (warning.code === "CIRCULAR_DEPENDENCY") return;
    if (warning.code === "THIS_IS_UNDEFINED") return;
    warn(warning);
  },
};
