function handle_menu(contentId) {
  const content = document.getElementById(contentId);
  if (!content) return

  const overlay = document.createElement("div");
  overlay.id = `dropdown-menu-overlay-${contentId}`
  overlay.classList.add("dropdown-menu-overlay")
  overlay.addEventListener("click", () => {
    handle_menu(contentId)
  })

  if (content.classList.contains("hidden")) {
    document.body.appendChild(overlay)
    content.classList.replace("hidden", "flex");
    content.classList.remove("animate-dropdown-close");
    content.classList.add("animate-dropdown-show");
    return;
  }
  if (content.classList.contains("flex")) {
    document.getElementById(`dropdown-menu-overlay-${contentId}`).remove()
    content.classList.remove("animate-dropdown-show");
    content.classList.add("animate-dropdown-close");
    setTimeout(() => {
      content.classList.replace("flex", "hidden");
    }, 500);
    return;
  }
}
