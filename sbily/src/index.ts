import "./index.css";

import type { WindowWithCustomProps } from "./types";
import { dialog, initDialog } from "./components/dialog";
import { initDropdownMenu } from "./components/dropdownMenu";
import { closeToast, toast } from "./components/toast";
import { copy } from "./utils/copy";
import "./components/links/select";

const windowExtensions: WindowWithCustomProps = {
  copy,
  toast,
  closeToast,
  dialog,
};

Object.assign(window, windowExtensions);

const initApp = (): void => {
  initDialog();
  initDropdownMenu();
};

document.addEventListener("DOMContentLoaded", initApp);
