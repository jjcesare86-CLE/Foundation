/*
 * Switchboard widget v1 -- SWITCHBOARD_BUILD.md Phase 1.
 * Self-contained, zero external runtime deps, Shadow DOM (zero CSS bleed).
 * Embed: <script src="{foundation}/switchboard/v1.js" data-tenant-key="pk_..." data-foundation-url="https://..." defer></script>
 *
 * Auth bridge: the host page must set window.__switchboardGetHostToken to an
 * async function returning its own Supabase Auth access_token before this
 * script runs (the "dashboard SDK helper" from §3.1). This file exchanges
 * that for a Switchboard JWT via POST /switchboard/auth/exchange and holds
 * it in memory only (not localStorage -- short-lived by design, re-exchange
 * on reload).
 *
 * Scope note (Phase 1, honest about what's NOT here yet): no WS/SSE
 * presence/proactive-DM channel (P2), no voice call button (P3), no
 * locked-agent checkout flow (P5). Presence line always reads a static
 * "idle" for now -- real presence needs the P2 events channel.
 */
(function () {
  "use strict";

  var CURRENT_SCRIPT = document.currentScript;
  var FOUNDATION_URL = (CURRENT_SCRIPT && CURRENT_SCRIPT.dataset.foundationUrl) || "";
  var TENANT_KEY = (CURRENT_SCRIPT && CURRENT_SCRIPT.dataset.tenantKey) || "";

  if (!FOUNDATION_URL) {
    console.error("[switchboard] data-foundation-url is required on the script tag");
    return;
  }

  var state = {
    token: null,
    workspaceId: null,
    roster: [],
    pins: [],
    settings: { bubble_color: "#B4672B", lang: "en", corner: "bottom-left" },
    expanded: false,
    activeAgent: null,
    threads: {}, // agent_slug -> {messages: [...]}
  };

  function css() {
    return (
      ":host{all:initial}" +
      "*{box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}" +
      ".fab{position:fixed;bottom:20px;left:20px;width:56px;height:56px;border-radius:50%;" +
      "background:linear-gradient(135deg,#B4672B,#D48A47);color:#fff;border:none;cursor:pointer;" +
      "box-shadow:0 4px 14px rgba(0,0,0,.25);font-weight:600;font-size:18px;z-index:999999;" +
      "display:flex;align-items:center;justify-content:center}" +
      ".badge{position:absolute;top:-4px;right:-4px;background:#c0392b;color:#fff;border-radius:10px;" +
      "min-width:18px;height:18px;font-size:11px;display:flex;align-items:center;justify-content:center;padding:0 4px}" +
      ".panel{position:fixed;bottom:88px;left:20px;width:320px;max-height:70vh;background:#fff;" +
      "border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.25);display:flex;flex-direction:column;" +
      "overflow:hidden;z-index:999999;border:1px solid #e5e5e5}" +
      ".panel[hidden]{display:none}" +
      ".hdr{padding:10px 14px;background:linear-gradient(90deg,rgba(180,103,43,.14),rgba(47,95,168,.13));" +
      "font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}" +
      ".hdr button{background:none;border:none;cursor:pointer;font-size:16px;color:#666}" +
      ".list{overflow-y:auto;flex:1}" +
      ".grp{font-size:11px;text-transform:uppercase;color:#888;padding:8px 14px 4px;font-weight:600}" +
      ".row{display:flex;align-items:center;gap:8px;padding:8px 14px;cursor:pointer}" +
      ".row:hover{background:#f7f7f7}" +
      ".row.locked{opacity:.55;cursor:default}" +
      ".av{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#B4672B,#D48A47);" +
      "color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0}" +
      ".meta{flex:1;min-width:0}" +
      ".name{font-size:13px;font-weight:600;color:#222;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
      ".role{font-size:11px;color:#888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
      ".lock{font-size:14px;color:#aaa}" +
      ".unread{background:#2F5FA8;color:#fff;border-radius:9px;min-width:16px;height:16px;font-size:10px;" +
      "display:flex;align-items:center;justify-content:center;padding:0 4px}" +
      ".chat{position:fixed;bottom:20px;left:350px;width:320px;height:440px;background:#fff;" +
      "border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.25);display:flex;flex-direction:column;" +
      "overflow:hidden;z-index:999999;border:1px solid #e5e5e5}" +
      ".chat[hidden]{display:none}" +
      ".chat .hdr{background:linear-gradient(90deg,rgba(180,103,43,.14),#fff)}" +
      ".msgs{flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:8px}" +
      ".msg{max-width:80%;padding:7px 10px;border-radius:10px;font-size:13px;line-height:1.4}" +
      ".msg.user{align-self:flex-end;background:#B4672B;color:#fff}" +
      ".msg.agent{align-self:flex-start;background:#f0f0f0;color:#222}" +
      ".composer{display:flex;border-top:1px solid #eee;padding:8px}" +
      ".composer input{flex:1;border:1px solid #ddd;border-radius:6px;padding:7px 9px;font-size:13px}" +
      ".composer button{margin-left:6px;border:none;background:#B4672B;color:#fff;border-radius:6px;" +
      "padding:0 12px;cursor:pointer;font-weight:600}" +
      ".err{color:#c0392b;font-size:12px;padding:8px 14px}"
    );
  }

  async function exchangeAuth() {
    if (typeof window.__switchboardGetHostToken !== "function") {
      throw new Error("window.__switchboardGetHostToken is not set by the host page");
    }
    var hostToken = await window.__switchboardGetHostToken();
    var resp = await fetch(FOUNDATION_URL + "/switchboard/auth/exchange", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: hostToken, host: "an" }),
    });
    if (!resp.ok) throw new Error("switchboard auth exchange failed: " + resp.status);
    return resp.json();
  }

  function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ Authorization: "Bearer " + state.token, "Content-Type": "application/json" }, opts.headers || {});
    return fetch(FOUNDATION_URL + path, opts).then(function (r) {
      if (!r.ok) return r.json().then(function (b) { throw new Error(b.detail || r.status); });
      return r.json();
    });
  }

  function initials(name) {
    return (name || "?").split(/\s+/).map(function (w) { return w[0]; }).join("").slice(0, 2).toUpperCase();
  }

  var root, shadow, fab, panel, chatWin;

  function render() {
    var badgeCount = state.roster.reduce(function (n, a) { return n + (a.unread || 0); }, 0);
    fab.innerHTML = "AI" + (badgeCount ? '<span class="badge">' + badgeCount + "</span>" : "");

    var pinnedSlugs = state.pins.map(function (p) { return p.agent_slug; });
    var byDept = {};
    state.roster.forEach(function (a) {
      var d = a.department_label || a.department || "Other";
      (byDept[d] = byDept[d] || []).push(a);
    });

    var html = '<div class="hdr">Your Team<button data-close-panel>&times;</button></div><div class="list">';
    if (pinnedSlugs.length) {
      html += '<div class="grp">Pinned</div>';
      state.roster.filter(function (a) { return pinnedSlugs.indexOf(a.id) !== -1; }).forEach(function (a) { html += rowHtml(a); });
    }
    Object.keys(byDept).sort().forEach(function (d) {
      html += '<div class="grp">' + d + "</div>";
      byDept[d].forEach(function (a) { html += rowHtml(a); });
    });
    html += "</div>";
    panel.innerHTML = html;
    panel.querySelector("[data-close-panel]").onclick = function () { toggle(false); };
    panel.querySelectorAll(".row[data-agent]").forEach(function (el) {
      el.onclick = function () {
        var slug = el.getAttribute("data-agent");
        var locked = el.getAttribute("data-locked") === "1";
        if (locked) { openLockedUpsell(slug); return; }
        openChat(slug);
      };
    });
  }

  function rowHtml(a) {
    var locked = !a.unlocked;
    return (
      '<div class="row' + (locked ? " locked" : "") + '" data-agent="' + a.id + '" data-locked="' + (locked ? 1 : 0) + '">' +
      '<div class="av">' + initials(a.biblical_name || a.id) + "</div>" +
      '<div class="meta"><div class="name">' + (a.biblical_name || a.id) + '</div><div class="role">' + (a.role || "") + "</div></div>" +
      (locked ? '<span class="lock">&#128274;</span>' : a.unread ? '<span class="unread">' + a.unread + "</span>" : "") +
      "</div>"
    );
  }

  function openLockedUpsell(slug) {
    var a = state.roster.filter(function (x) { return x.id === slug; })[0];
    alert((a ? a.biblical_name || a.id : slug) + " is locked on your plan. (Upsell/checkout flow ships in Phase 5.)");
  }

  function toggle(force) {
    state.expanded = typeof force === "boolean" ? force : !state.expanded;
    panel.hidden = !state.expanded;
    if (!state.expanded) chatWin.hidden = true;
  }

  async function openChat(agentSlug) {
    state.activeAgent = agentSlug;
    var data = await api("/switchboard/threads/" + agentSlug);
    state.threads[agentSlug] = data;
    renderChat();
    chatWin.hidden = false;
  }

  function renderChat() {
    var agent = state.roster.filter(function (a) { return a.id === state.activeAgent; })[0] || {};
    var thread = state.threads[state.activeAgent] || { messages: [] };
    var html =
      '<div class="hdr"><span>' + (agent.biblical_name || state.activeAgent) + '</span><button data-close-chat>&times;</button></div>' +
      '<div class="msgs">' +
      thread.messages.map(function (m) {
        if (m.sender === "system") return "";
        return '<div class="msg ' + (m.sender === "user" ? "user" : "agent") + '">' + escapeHtml(m.body || "") + "</div>";
      }).join("") +
      '</div>' +
      '<div class="composer"><input type="text" placeholder="Message ' + (agent.biblical_name || "") + '..." /><button data-send>Send</button></div>';
    chatWin.innerHTML = html;
    chatWin.querySelector("[data-close-chat]").onclick = function () { chatWin.hidden = true; };
    var input = chatWin.querySelector("input");
    var send = function () {
      var text = input.value.trim();
      if (!text) return;
      input.value = "";
      var msgs = chatWin.querySelector(".msgs");
      msgs.insertAdjacentHTML("beforeend", '<div class="msg user">' + escapeHtml(text) + "</div>");
      msgs.scrollTop = msgs.scrollHeight;
      api("/switchboard/threads/" + state.activeAgent + "/messages", { method: "POST", body: JSON.stringify({ text: text }) })
        .then(function (r) {
          msgs.insertAdjacentHTML("beforeend", '<div class="msg agent">' + escapeHtml(r.reply.body) + "</div>");
          msgs.scrollTop = msgs.scrollHeight;
        })
        .catch(function (e) {
          msgs.insertAdjacentHTML("beforeend", '<div class="err">' + escapeHtml(String(e.message || e)) + "</div>");
        });
    };
    chatWin.querySelector("[data-send]").onclick = send;
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") send(); });
  }

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  async function boot() {
    root = document.createElement("div");
    root.id = "switchboard-widget-root";
    document.body.appendChild(root);
    shadow = root.attachShadow({ mode: "open" });
    var style = document.createElement("style");
    style.textContent = css();
    shadow.appendChild(style);

    fab = document.createElement("button");
    fab.className = "fab";
    fab.onclick = function () { toggle(); };
    shadow.appendChild(fab);

    panel = document.createElement("div");
    panel.className = "panel";
    panel.hidden = true;
    shadow.appendChild(panel);

    chatWin = document.createElement("div");
    chatWin.className = "chat";
    chatWin.hidden = true;
    shadow.appendChild(chatWin);

    try {
      var ex = await exchangeAuth();
      state.token = ex.token;
      state.workspaceId = ex.workspace_id;
      var bootstrap = await api("/switchboard/bootstrap");
      state.roster = bootstrap.roster;
      state.pins = bootstrap.pins;
      state.settings = bootstrap.settings;
      render();
    } catch (e) {
      console.error("[switchboard] failed to initialize:", e);
      fab.title = "Switchboard unavailable: " + e.message;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.Switchboard = { toggle: toggle, tenantKey: TENANT_KEY };
})();
