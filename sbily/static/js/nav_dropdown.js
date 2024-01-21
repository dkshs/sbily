document.addEventListener("DOMContentLoaded", () => {
  const trigger = document.getElementById("nav__dropdown-trigger");
  const content = document.getElementById("nav__dropdown-content");
  if (!trigger || !content) return;

  trigger.addEventListener("click", () => {
    if (content.classList.contains("flex")) {
      content.classList.remove("animate-dropdown-show");
      content.classList.add("animate-dropdown-close");
      setTimeout(() => {
        content.classList.replace("flex", "hidden");
      }, 500);
      return;
    }
    if (content.classList.contains("hidden")) {
      content.classList.replace("hidden", "flex");
      content.classList.remove("animate-dropdown-close");
      content.classList.add("animate-dropdown-show");
      return;
    }
  });
});
