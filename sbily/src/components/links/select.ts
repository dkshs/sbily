import { dialog } from "../dialog";
import { toast } from "../toast";

const tbody = document.getElementById("tbody");
const checkAllLinksCheckbox = document.getElementById(
  "check-all-links",
) as HTMLInputElement;

const linkActionGo = document.getElementById("link-action-go");
linkActionGo?.addEventListener("click", (e) => {
  if (!e.target) return;
  if (!tbody) return;

  const action = (document.getElementById("action") as HTMLSelectElement).value;
  if (action === "" || action === "------------") {
    toast("No action selected!", "toast-warning");
    return;
  }

  const checkedLinks = tbody.querySelectorAll("input:checked");
  if (checkedLinks?.length === 0) {
    toast("No links selected!", "toast-warning");
    return;
  }

  const actionType = action.split("_")[0];
  document.getElementById("action-text")!.textContent = actionType;
  document.getElementById("action-text-f")!.textContent = `${actionType}d`;

  const linksSelectedUl = document.getElementById("links-selected-ul");
  linksSelectedUl!.innerHTML = "";
  checkedLinks?.forEach((checkbox) => {
    const li = document.createElement("li");
    const content = document.createElement("span");
    content.textContent = (checkbox as HTMLInputElement).dataset.link || "";
    content.classList.add("text-primary");
    li.innerHTML = `Link: ${content.outerHTML}`;
    linksSelectedUl!.append(li);
  });

  const dialogTarget = (e.target as HTMLElement).dataset.jswcTarget;
  if (!dialogTarget) return;
  const targetElement = document.getElementById(dialogTarget);
  if (!targetElement) return;
  dialog(targetElement);
});

function updateActionCounter() {
  const actionCounter = document.getElementById("action-counter");
  const actionCount = tbody?.querySelectorAll("input:checked");
  actionCounter!.textContent = actionCount?.length.toString() || "0";
}

function checkLink(checkbox: HTMLInputElement) {
  if (!checkbox.checked) {
    checkAllLinksCheckbox.checked = false;
  }

  const link = checkbox.closest("tr");
  link?.classList.toggle("selected");
  link?.classList.toggle("hover:bg-muted/50");
  updateActionCounter();
}

function checkAllLinks() {
  const isChecked = checkAllLinksCheckbox?.checked;

  tbody?.querySelectorAll("tr").forEach((link) => {
    link.querySelectorAll("input").forEach((checkbox) => {
      if (isChecked) {
        link.classList.add("selected");
        link.classList.remove("hover:bg-muted/50");
      } else {
        link.classList.remove("selected");
        link.classList.add("hover:bg-muted/50");
      }
      (checkbox as HTMLInputElement).checked = isChecked;
    });
  });

  updateActionCounter();
}

checkAllLinksCheckbox?.addEventListener("change", checkAllLinks);
document.addEventListener("DOMContentLoaded", () => {
  const linksCheckbox = document.querySelectorAll("input[data-link]");
  linksCheckbox.forEach((checkbox) => {
    checkbox.addEventListener("change", (e) =>
      checkLink(e.target as HTMLInputElement),
    );
  });
});
