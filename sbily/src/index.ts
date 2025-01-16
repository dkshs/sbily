import "./index.css";

import { dialog, initDialog } from "./components/dialog";
import { initDropdownMenu } from "./components/dropdownMenu";
import { closeToast, toast } from "./components/toast";
import { copy } from "./utils/copy";
import "./components/links/select";

declare global {
  interface Window {
    copy: typeof copy;
    toast: typeof toast;
    closeToast: typeof closeToast;
    dialog: typeof dialog;
  }
}

Object.assign(window, {
  copy,
  toast,
  closeToast,
  dialog,
});

document.addEventListener("DOMContentLoaded", () => {
  initDialog();
  initDropdownMenu();
});
