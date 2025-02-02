export function initTabs() {
  const tabLists = document.querySelectorAll<HTMLDivElement>(
    "[data-jwsc-tab-list]",
  );

  tabLists.forEach((tabs) => {
    tabs.role = "tablist";

    const tabUrlQuery = tabs.dataset.jwscTabUrlQuery;
    const tabDefault = tabs.dataset.jwscTabDefault;

    const tabButtons = tabs.querySelectorAll<HTMLButtonElement>(
      "[data-jwsc-tab-value]",
    );
    const tabPanels = document.querySelectorAll<HTMLDivElement>(
      "[data-jwsc-tab-panel]",
    );

    tabButtons.forEach((button) => {
      button.role = "tab";
      button.ariaSelected = "false";

      button.addEventListener("click", () => {
        const target = button.dataset.jwscTabValue;
        const targetElement =
          target && document.querySelector(`[data-jwsc-tab-panel=${target}]`);
        if (!targetElement) return;

        button.dataset.state = "active";
        button.ariaSelected = "true";
        tabPanels.forEach((panel) => {
          panel.dataset.state =
            panel.dataset.jwscTabPanel === target ? "active" : "inactive";
        });
        tabButtons.forEach((otherButton) => {
          if (otherButton !== button) {
            otherButton.dataset.state = "inactive";
            otherButton.ariaSelected = "false";
          }
        });
      });
    });

    if (tabDefault) {
      const defaultButton = tabs.querySelector<HTMLButtonElement>(
        `[data-jwsc-tab-value=${tabDefault}]`,
      );
      if (defaultButton) defaultButton.click();
    }

    if (tabUrlQuery) {
      const urlParams = new URLSearchParams(window.location.search);
      const tabParam = urlParams.get(tabUrlQuery);
      if (tabParam) {
        const tabButton = tabs.querySelector<HTMLButtonElement>(
          `[data-jwsc-tab-value=${tabParam}]`,
        );
        if (tabButton) tabButton.click();
      }
    }
  });
}
