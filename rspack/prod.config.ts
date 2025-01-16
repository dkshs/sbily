import { merge } from "webpack-merge";
import { commonConfig } from "./common.config";

const staticUrl = `https://storage.googleapis.com/${process.env.DJANGO_GCP_STORAGE_BUCKET_NAME}/static/`;

export default merge(commonConfig, {
  mode: "production",
  devtool: "source-map",
  bail: true,
  output: {
    publicPath: `${staticUrl}rspack_bundles/`,
  },
});
