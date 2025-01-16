import { dkshs } from "@dkshs/eslint-config";

export default dkshs({
  ignores: ["**/*.html"],
  toml: {
    overrides: { "toml/indent": ["error", 4] },
  },
});
