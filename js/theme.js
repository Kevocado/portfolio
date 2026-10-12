/* theme.js — switches the site's visual edition.
   Sets data-theme on <html> and persists the choice in localStorage.
   A tiny inline script in <head> applies the saved value before first paint. */
(function () {
  "use strict";

  var THEMES = ["editorial", "darkroom", "terminal"];
  var STORAGE_KEY = "ksigey-edition";
  var root = document.documentElement;

  function isValid(name) {
    return THEMES.indexOf(name) !== -1;
  }

  function readStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function store(name) {
    try {
      localStorage.setItem(STORAGE_KEY, name);
    } catch (e) {
      /* private mode etc. — the theme still applies for this visit */
    }
  }

  function apply(name) {
    if (!isValid(name)) {
      name = "editorial";
    }
    root.setAttribute("data-theme", name);
    store(name);
    var buttons = document.querySelectorAll("[data-set-theme]");
    for (var i = 0; i < buttons.length; i++) {
      var active = buttons[i].getAttribute("data-set-theme") === name;
      buttons[i].setAttribute("aria-pressed", active ? "true" : "false");
    }
  }

  // Honor the persisted choice (the <head> snippet usually beat us to it).
  var saved = readStored();
  if (isValid(saved) && root.getAttribute("data-theme") !== saved) {
    apply(saved);
  } else {
    // Normalize aria-pressed against the current theme.
    apply(root.getAttribute("data-theme") || "editorial");
  }

  var buttons = document.querySelectorAll("[data-set-theme]");
  for (var j = 0; j < buttons.length; j++) {
    (function (btn) {
      btn.addEventListener("click", function () {
        apply(btn.getAttribute("data-set-theme"));
      });
    })(buttons[j]);
  }

  // Exposed for console/debugging only.
  window.__setEdition = apply;
})();
