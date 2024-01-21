function verifyToastOl() {
  const toastOl = document.getElementById("toast-ol");
  if (!toastOl) {
    toastOl = document.createElement("ol");
    toastOl.setAttribute("id", "toast-ol");
    toastOl.setAttribute("tabindex", "-1");
    toastOl.classList.add("toast-list");
    document.body.appendChild(toastOl);
  }
  return toastOl;
}

function closeToast(id, time = 3000) {
  setTimeout(() => {
    const toast = document.getElementById(id);
    if (!toast) return;
    toast.classList.add("toast-close");
    setTimeout(() => toast.remove(), 600);
  }, time);
}

function getToastIcon(tag) {
  switch (tag) {
    case "toast-success":
      return '<i class="ph-fill ph-check-circle toast-icon"></i>';
    case "toast-warning":
      return '<i class="ph-fill ph-warning toast-icon"></i>';
    case "toast-error":
      return '<i class="ph-fill ph-warning-circle toast-icon"></i>';
    default:
      return '<i class="ph-fill ph-info toast-icon"></i>';
  }
}

function toast(msg, className, time = 3000) {
  const toastOl = verifyToastOl();
  id =
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15);
  toastOl.insertAdjacentHTML(
    "beforeend",
    `<li class="toast-open ${className}" id="${id}" role="alert" aria-live="assertive" aria-atomic="true" tabindex="0">
      <button
        type="button"
        onclick="closeToast('${id}', 0)"
        class="toast-close-btn"
        aria-label="Close toast"
        data-dismiss="toast"
        aria-hidden="true"
        tabindex="-1"
        role="button"
        aria-label="Close"
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
    </li>`
  );

  closeToast(id, time);
}
