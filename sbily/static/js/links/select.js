const tbody = document.getElementById("tbody");
const check_all_links_checkbox = document.getElementById("check_all_links");

document.getElementById("link_action_go").addEventListener("click", (event) => {
  const action = document.getElementById("action").value;
  if (action === "" || action === "------------") {
    toast("No action selected!", "toast-warning");
    return;
  };

  const checked_links = tbody.querySelectorAll("input:checked");
  if (checked_links.length === 0) {
    toast("No links selected!", "toast-warning");
    return;
  };

  const action_text = action.split("_")[0];
  document.getElementById("action_text").innerText = action_text;
  document.getElementById("action_text_f").innerText = `${action_text}d`;

  const links_selected_ul = document.getElementById("links_selected_ul");
  links_selected_ul.innerHTML = "";
  checked_links.forEach((link) => {
    const li = document.createElement("li");
    const content = document.createElement("span");
    content.innerText = link.getAttribute("data-link");
    content.classList.add("text-primary");
    li.innerHTML = `Link: ${content.outerHTML}`;
    links_selected_ul.appendChild(li);
  });

  const dialog_target = event.target.getAttribute("data-jswc-target");
  const target_element = document.getElementById(dialog_target);
  dialog(target_element);
});

function update_action_counter() {
  const actionCounter = document.getElementById("action_counter");
  const checked_links = tbody.querySelectorAll("input:checked");
  actionCounter.innerText = checked_links.length;
};

function check_all_links() {
  const check_all_links_checked = check_all_links_checkbox.checked;

  tbody.querySelectorAll("tr").forEach((link) => {
    link.querySelectorAll("input").forEach((checkbox) => {
      if (check_all_links_checked) {
        link.classList.add("selected");
        link.classList.remove("hover:bg-muted/50");
      } else {
        link.classList.remove("selected");
        link.classList.add("hover:bg-muted/50");
      };
      checkbox.checked = check_all_links_checked;
    });
  });

  update_action_counter();
};

function check_link(id) {
  const link = document.getElementById(id);
  if (!document.getElementById(`check_link_${id}`).checked) {
    check_all_links_checkbox.checked = false;
  };
  link.classList.toggle("selected");
  link.classList.toggle("hover:bg-muted/50");

  update_action_counter();
};

check_all_links_checkbox.addEventListener("change", check_all_links);
