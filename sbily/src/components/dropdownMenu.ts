import type { EventHandler } from "@/types";

interface DropdownMenuOptions {
  animation?: boolean;
  closeOnEscape?: boolean;
  closeOnOverlayClick?: boolean;
}

const DEFAULT_OPTIONS: DropdownMenuOptions = {
  animation: false,
  closeOnEscape: true,
  closeOnOverlayClick: true,
};

export function initDropdownMenu() {
  const dropdownButtons = document.querySelectorAll<HTMLElement>(
    "[data-jswc-dropdown]",
  );

  dropdownButtons.forEach((button) => {
    const target = button.dataset.jswcTarget;
    if (!target) return;

    const targetElement = document.getElementById(target);
    if (!targetElement) return;

    button.setAttribute("aria-expanded", "false");
    targetElement.setAttribute("aria-hidden", "true");
    targetElement.setAttribute("tabindex", "-1");
    targetElement.setAttribute("role", "menu");

    const options: DropdownMenuOptions = {
      ...DEFAULT_OPTIONS,
      animation: targetElement.dataset.jswcDropdownAnimation === "true",
    };

    button.addEventListener("click", () =>
      dropdownMenu(targetElement, options),
    );
  });
}

function createOverlay(
  targetElement: HTMLElement,
  options: DropdownMenuOptions,
): HTMLElement {
  const overlayId = `dropdown-overlay-${targetElement.id}`;

  const existingOverlay = document.getElementById(overlayId);
  if (existingOverlay) return existingOverlay;

  const overlay = document.createElement("div");
  overlay.id = overlayId;
  overlay.classList.add("dropdown-menu-overlay");
  overlay.setAttribute("aria-hidden", "false");

  if (options.closeOnOverlayClick) {
    overlay.addEventListener("click", () =>
      dropdownMenu(targetElement, options),
    );
  }

  return overlay;
}

export function dropdownMenu(
  targetElement: HTMLElement,
  options: DropdownMenuOptions = DEFAULT_OPTIONS,
): void {
  const handleKeydown: EventHandler<KeyboardEvent> = (event) => {
    if (event.key === "Escape") {
      dropdownMenu(targetElement);
    }
  };

  const handleFocusout: EventHandler<FocusEvent> = (event) => {
    if (!targetElement.contains(event.relatedTarget as Node)) {
      dropdownMenu(targetElement);
    }
  };

  const cleanup = () => {
    document.removeEventListener("keydown", handleKeydown);
    document.removeEventListener("focus", handleFocusout, true);
  };

  let overlay = createOverlay(targetElement, options);
  const isOpen = targetElement.getAttribute("aria-hidden") !== "true";
  const triggerButton = document.querySelector<HTMLElement>(
    `[data-jswc-target="${targetElement.id}"]`,
  );

  if (triggerButton) {
    triggerButton.setAttribute("aria-expanded", (!isOpen).toString());
  }

  document.addEventListener("keydown", handleKeydown);
  targetElement.addEventListener("focusout", handleFocusout);

  if (!isOpen) {
    document.body.append(overlay);

    targetElement.setAttribute("aria-hidden", "false");
    targetElement.classList.replace("hidden", "flex");
  } else {
    targetElement.setAttribute("aria-hidden", "true");

    overlay = createOverlay(targetElement, options);
    overlay.setAttribute("aria-hidden", "true");

    const closeDropdownMenu = () => {
      overlay.remove();
      targetElement.classList.replace("flex", "hidden");
      cleanup();
    };

    if (options.animation) {
      setTimeout(() => requestAnimationFrame(closeDropdownMenu), 200);
    } else {
      closeDropdownMenu();
    }
  }
}
