document.addEventListener("DOMContentLoaded", () => {
  const dialogButtons = document.querySelectorAll("[data-jswc-dialog]");

  dialogButtons.forEach((button) => {
    const target = button.dataset.jswcTarget;
    if (!target) return;

    const targetElement = document.getElementById(target);
    if (!targetElement) return;

    targetElement.ariaHidden = "true";
    targetElement.tabIndex = "-1";

    button.addEventListener("click", () => dialog(targetElement));
  });
});

function create_overlay(targetElement) {
  const overlayId = `dialog-overlay-${targetElement.id}`;

  let overlay = document.getElementById(overlayId);
  if (overlay) return overlay;

  overlay = document.createElement("div");
  overlay.id = overlayId;
  overlay.classList.add("dialog-overlay");
  overlay.setAttribute("aria-hidden", "false");
  overlay.addEventListener("click", () => dialog(targetElement));

  return overlay;
}

/**
 * @param {HTMLElement} targetElement The dialog element to toggle.
 */
function dialog(targetElement) {
  let overlay = create_overlay(targetElement);

  const isOpen = targetElement.ariaHidden != "true";

  const closeButtons = targetElement.querySelectorAll(
    "[data-jswc-dialog-close]",
  );
  closeButtons.forEach((button) => {
    button.addEventListener("click", () => dialog(targetElement));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key == "Escape") {
      dialog(targetElement);
    }
  });
  document.addEventListener(
    "focus",
    (event) => {
      if (!targetElement.contains(event.target)) {
        event.stopPropagation();
        targetElement.focus();
      }
    },
    true,
  );

  const addAnimation = targetElement.dataset.jswcDialogAnimation == "true";

  if (!isOpen) {
    if (document.body.scrollHeight > window.innerHeight) {
      document.body.style.overflow = "hidden";
      document.body.style.paddingRight = "17px";
    }
    document.body.append(overlay);

    targetElement.ariaHidden = "false";
    targetElement.ariaModal = "true";
    targetElement.role = "dialog";

    targetElement.classList.replace("hidden", "block");
  } else {
    targetElement.ariaHidden = "true";
    targetElement.removeAttribute("aria-modal");
    targetElement.removeAttribute("role");

    overlay = create_overlay(targetElement);
    overlay.ariaHidden = "true";

    setTimeout(
      () => {
        document.body.style.removeProperty("overflow");
        document.body.style.removeProperty("padding-right");
        overlay.remove();

        targetElement.classList.replace("block", "hidden");
      },
      addAnimation ? 200 : 0,
    );
  }
}
