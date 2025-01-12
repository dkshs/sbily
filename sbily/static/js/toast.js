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

function closeToast(id, time = 3000) {
  const toast = document.getElementById(id);
  if (!toast) return;

  const timeout = setTimeout(() => {
    toast.classList.add("toast-close");
    setTimeout(() => toast.remove(), 600);
  }, time);

  toast.addEventListener("mouseenter", () => clearTimeout(timeout));
  toast.addEventListener("mouseleave", () => closeToast(id, time));
}

function getToastIcon(tag) {
  const icon = (i) => `<i class="ph-fill ph-${i} toast-icon"></i>`;
  switch (tag) {
    case "toast-success":
      return icon("check-circle");
    case "toast-warning":
      return icon("warning");
    case "toast-error":
      return icon("warning-circle");
    default:
      return icon("info");
  }
}

function toast(msg, className, time = 3000) {
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
