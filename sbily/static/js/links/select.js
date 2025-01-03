const tbody = document.getElementById("tbody");
const check_all_links_checkbox = document.getElementById("check_all_links");

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
