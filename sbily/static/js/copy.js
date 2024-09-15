function copy(value, btnId) {
  const button = document.querySelector(`#${btnId}`);
  const buttonContent = button.innerHTML;
  button.setAttribute("disabled", true);
  const successIcon = `<i class="ph-bold ph-check"></i>`;
  const errorIcon = `<i class="ph-bold ph-x"></i>`;

  try {
    navigator.clipboard.writeText(value);
    button.innerHTML = `${successIcon} Copied`;
    toast("Copied to clipboard", "toast-success");
  } catch (error) {
    toast("Failed to copy", "toast-error");
    button.innerHTML = `${errorIcon} Error`;
    console.error(error);
    return;
  }

  setTimeout(() => {
    button.innerHTML = buttonContent;
    button.removeAttribute("disabled");
  }, 2000);
}
