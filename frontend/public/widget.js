(function () {
  "use strict";

  var script = document.currentScript;
  if (!script) {
    var scripts = document.querySelectorAll("script[src*='widget.js'][data-id]");
    script = scripts[scripts.length - 1];
  }

  var widgetId = script && script.getAttribute("data-id");
  if (!widgetId) return;

  var configuredBase = (script && script.getAttribute("data-api-base")) || window.NEXT_PUBLIC_API_BASE_URL || "https://letrusto.com";
  var apiBase = configuredBase.replace(/\/$/, "");
  if (!/\/api\/v1$/.test(apiBase)) apiBase += "/api/v1";

  function addStyles() {
    if (document.getElementById("letrusto-widget-styles")) return;
    var style = document.createElement("style");
    style.id = "letrusto-widget-styles";
    style.textContent = [
      ".letrusto-proof-widget{position:fixed;z-index:2147483647;display:none;max-width:min(360px,calc(100vw - 32px));box-sizing:border-box;padding:14px 16px;border:1px solid rgba(15,23,42,.1);border-radius:12px;background:#fff;color:#0f172a;box-shadow:0 12px 36px rgba(15,23,42,.18);font:14px/1.4 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;opacity:0;transform:translateY(10px);transition:opacity .35s ease,transform .35s ease}",
      ".letrusto-proof-widget.letrusto-proof-visible{opacity:1;transform:translateY(0)}",
      ".letrusto-proof-widget.letrusto-proof-bottom-left{left:16px;bottom:16px}",
      ".letrusto-proof-widget.letrusto-proof-bottom-right{right:16px;bottom:16px}",
      ".letrusto-proof-widget.letrusto-proof-top-left{left:16px;top:16px}",
      ".letrusto-proof-widget.letrusto-proof-top-right{right:16px;top:16px}",
      ".letrusto-proof-row{display:flex;align-items:flex-start;gap:10px}",
      ".letrusto-proof-avatar{width:32px;height:32px;flex:none;border-radius:50%;object-fit:cover;background:#e2e8f0}",
      ".letrusto-proof-copy{min-width:0}.letrusto-proof-name{font-weight:700}.letrusto-proof-location{color:#64748b;font-size:12px}.letrusto-proof-action{margin-top:2px}.letrusto-proof-review{margin-top:6px;color:#475569;font-size:13px}.letrusto-proof-rating{margin-top:4px;color:var(--letrusto-proof-color,#2563eb);letter-spacing:1px}"
    ].join("");
    document.head.appendChild(style);
  }

  function text(value) {
    return value == null ? "" : String(value);
  }

  function render(container, event, color) {
    container.style.setProperty("--letrusto-proof-color", color || "#2563eb");
    container.replaceChildren();
    var row = document.createElement("div");
    row.className = "letrusto-proof-row";

    if (event.avatar_url) {
      var avatar = document.createElement("img");
      avatar.className = "letrusto-proof-avatar";
      avatar.alt = "";
      avatar.src = event.avatar_url;
      row.appendChild(avatar);
    }

    var copy = document.createElement("div");
    copy.className = "letrusto-proof-copy";
    var name = document.createElement("div");
    name.className = "letrusto-proof-name";
    name.textContent = text(event.customer_name);
    copy.appendChild(name);

    if (event.customer_location) {
      var location = document.createElement("div");
      location.className = "letrusto-proof-location";
      location.textContent = text(event.customer_location);
      copy.appendChild(location);
    }

    if (event.action_text) {
      var action = document.createElement("div");
      action.className = "letrusto-proof-action";
      action.textContent = text(event.action_text);
      copy.appendChild(action);
    }

    if (event.rating) {
      var rating = document.createElement("div");
      rating.className = "letrusto-proof-rating";
      rating.textContent = "★".repeat(Math.max(0, Math.min(5, Number(event.rating))));
      copy.appendChild(rating);
    }

    if (event.review_text) {
      var review = document.createElement("div");
      review.className = "letrusto-proof-review";
      review.textContent = text(event.review_text);
      copy.appendChild(review);
    }

    row.appendChild(copy);
    container.appendChild(row);
  }

  function start(data) {
    if (!data || !Array.isArray(data.events) || data.events.length === 0) return;
    addStyles();
    var container = document.createElement("aside");
    container.className = "letrusto-proof-widget letrusto-proof-" + (data.position || "bottom-left");
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-label", "Recent customer activity");
    document.body.appendChild(container);

    var delay = Math.max(1, Number(data.display_delay) || 3) * 1000;
    var index = 0;
    function show() {
      render(container, data.events[index], data.theme_color);
      container.style.display = "block";
      requestAnimationFrame(function () { container.classList.add("letrusto-proof-visible"); });
      window.setTimeout(function () {
        container.classList.remove("letrusto-proof-visible");
        window.setTimeout(function () {
          index = (index + 1) % data.events.length;
          show();
        }, 350);
      }, delay);
    }
    show();
  }

  fetch(apiBase + "/public/embed/" + encodeURIComponent(widgetId), { headers: { Accept: "application/json" } })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(start)
    .catch(function () { /* A marketing widget must fail silently. */ });
}());
