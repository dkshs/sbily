function verifyToastOl() {
  let toastOl = document.getElementById("toast-ol");
  if (!toastOl) {
    toastOl = document.createElement("ol");
    toastOl.setAttribute("id", "toast-ol");
    toastOl.setAttribute("tabindex", "-1");
    toastOl.classList.add("toast-list");
    document.body.append(toastOl);
  }
  return toastOl;
}

function getIcon(iconName: string) {
  return `<i class="ph-fill ph-${iconName} toast-icon"></i>`;
}
function getToastIcon(tag: string) {
  switch (tag) {
    case "toast-success":
      return getIcon("check-circle");
    case "toast-warning":
      return getIcon("warning");
    case "toast-error":
      return getIcon("warning-circle");
    default:
      return getIcon("info");
  }
}

export function closeToast(id: string, time = 3000) {
  const toast = document.getElementById(id);
  if (!toast) return;

  const timeout = setTimeout(() => {
    toast.classList.add("toast-close");
    setTimeout(() => toast.remove(), 600);
  }, time);

  toast.addEventListener("mouseenter", () => clearTimeout(timeout));
  toast.addEventListener("mouseleave", () => closeToast(id, time));
}

export function toast(msg: string, className: string, time = 3000) {
  const toastOl = verifyToastOl();
  const id = `toast-${Date.now()}`;
  toastOl.insertAdjacentHTML(
    "beforeend",
    `<li class="toast-open ${className}" id="${id}" role="alert" aria-live="assertive" aria-atomic="true" tabindex="0">
      <button
        type="button"
        onclick="closeToast('${id}', 0)"
        class="toast-close-btn"
        aria-label="Close toast"
        data-dismiss="toast"
      >
        <span aria-hidden="true">&times;</span>
      </button>
      <div class="flex items-center">
        ${getToastIcon(className)}
        <p
          class="toast-msg"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          ${msg}
        </p>
      </div>
    </li>`,
  );

  closeToast(id, time);
}
