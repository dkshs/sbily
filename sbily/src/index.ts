import "./index.css";

import type { WindowWithCustomProps } from "./types";
import { dialog, initDialog } from "./components/dialog";
import { initDropdownMenu } from "./components/dropdownMenu";
import { initSwitch, Switch } from "./components/switch";
import { initThemeToggle } from "./components/themeToggle";
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
  setTimeout(() => {
    document.documentElement.classList.replace("opacity-0", "opacity-100");
  }, 500);
  initDialog();
  initDropdownMenu();
  initSwitch();
  initThemeToggle();
};

document.addEventListener("DOMContentLoaded", initApp);
