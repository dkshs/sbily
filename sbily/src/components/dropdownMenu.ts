import { isMobile } from "@/utils/isMobile";

export function initDropdownMenu() {
  const dropdownButtons = document.querySelectorAll(
    "[data-jswc-dropdown]",
  ) as unknown as HTMLElement[];

  dropdownButtons.forEach((button) => {
    const target = button.dataset.jswcTarget;
    if (!target) return;

    const targetElement = document.getElementById(target);
    if (!targetElement) return;

    button.setAttribute("aria-expanded", "false");
    targetElement.setAttribute("aria-hidden", "true");
    targetElement.setAttribute("tabindex", "-1");

    button.addEventListener("click", () => dropdownMenu(targetElement));
  });
}

function create_overlay(targetElement: HTMLElement) {
  const overlayId = `dropdown-overlay-${targetElement.id}`;

  let overlay = document.getElementById(overlayId);
  if (overlay) return overlay;

  overlay = document.createElement("div");
  overlay.id = overlayId;
  overlay.classList.add("dropdown-menu-overlay");
  overlay.setAttribute("aria-hidden", "false");
  overlay.addEventListener("click", () => dropdownMenu(targetElement));

  return overlay;
}

export function dropdownMenu(targetElement: HTMLElement) {
  let overlay = create_overlay(targetElement);

  const isOpen = targetElement.ariaHidden !== "true";
  const addAnimation = targetElement.dataset.jswcDropdownAnimation === "true";

  const triggerButton = document.querySelector(
    `[data-jswc-target="${targetElement.id}"]`,
  ) as HTMLElement;
  triggerButton?.setAttribute("aria-expanded", isOpen ? "false" : "true");

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") dropdownMenu(targetElement);
  });
  targetElement.addEventListener("focusout", (event) => {
    if (!targetElement.contains(event.relatedTarget as Node)) {
      dropdownMenu(targetElement);
    }
  });

  if (!isOpen) {
    if (!isMobile() && document.body.scrollHeight > window.innerHeight) {
      document.body.style.overflow = "hidden";
      document.body.style.paddingRight = "17px";
    }
    document.body.append(overlay);

    targetElement.ariaHidden = "false";
    targetElement.role = "menu";

    targetElement.classList.replace("hidden", "flex");
  } else {
    targetElement.ariaHidden = "true";
    targetElement.removeAttribute("role");

    overlay = create_overlay(targetElement);
    overlay.ariaHidden = "true";

    setTimeout(
      () => {
        document.body.style.removeProperty("overflow");
        document.body.style.removeProperty("padding-right");
        overlay.remove();

        targetElement.classList.replace("flex", "hidden");
      },
      addAnimation ? 200 : 0,
    );
  }
}
