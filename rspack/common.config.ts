import * as path from "node:path";
import { defineConfig } from "@rspack/cli";
import { rspack } from "@rspack/core";
import * as BundleTracker from "webpack-bundle-tracker";

// Target browsers, see: https://github.com/browserslist/browserslist
const targets = ["chrome >= 87", "edge >= 88", "firefox >= 78", "safari >= 14"];

export const commonConfig = defineConfig({
  target: "web",
  context: path.join(__dirname, "../"),
  entry: {
    main: path.resolve(__dirname, "../sbily/src/index.ts"),
  },
  output: {
    path: path.resolve(__dirname, "../sbily/static/rspack_bundles/"),
    publicPath: "/static/rspack_bundles/",
    filename: "js/[name]-[fullhash].js",
    chunkFilename: "js/[name]-[hash].js",
    clean: true,
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(path.join(__dirname, "../")),
      filename: "webpack-stats.json",
    }),
    new rspack.CssExtractRspackPlugin({
      filename: "css/[name].[contenthash].css",
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        use: [
          {
            loader: "builtin:swc-loader",
            options: {
              jsc: { parser: { syntax: "ecmascript" } },
              env: { targets },
            },
          },
        ],
      },
      {
        test: /\.ts$/,
        use: [
          {
            loader: "builtin:swc-loader",
            options: {
              jsc: { parser: { syntax: "typescript" } },
              env: { targets },
            },
          },
        ],
      },
      {
        test: /\.css$/,
        use: [
          rspack.CssExtractRspackPlugin.loader,
          "css-loader",
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: ["postcss-preset-env", "autoprefixer", "tailwindcss"],
              },
            },
          },
        ],
      },
    ],
  },
  optimization: {
    minimizer: [
      new rspack.SwcJsMinimizerRspackPlugin(),
      new rspack.LightningCssMinimizerRspackPlugin({
        minimizerOptions: { targets },
      }),
    ],
  },
  resolve: {
    extensions: ["...", ".ts"],
  },
});
