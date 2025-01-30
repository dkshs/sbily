import "./index.css";

import type { WindowWithCustomProps } from "./types";
import { dialog, initDialog } from "./components/dialog";
import { initDropdownMenu } from "./components/dropdownMenu";
import { initSwitch, Switch } from "./components/switch";
import { closeToast, toast } from "./components/toast";
import { copy } from "./utils/copy";
import "./components/links/select";

const windowExtensions: WindowWithCustomProps = {
  copy,
  toast,
  closeToast,
  dialog,
  Switch,
};

Object.assign(window, windowExtensions);

const initApp = (): void => {
  initDialog();
  initDropdownMenu();
  initSwitch();
};

document.addEventListener("DOMContentLoaded", initApp);
