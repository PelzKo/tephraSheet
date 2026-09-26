/* Breakdown popovers for composite values: hover on mouse devices, click/tap everywhere.
   Any other sheet element with a hover title (truncated text, racial traits, locations) shows
   that text in the same popover on click/tap, so everything works on tablets too. */
(function () {
  const pop = document.createElement("div");
  pop.className = "bd-pop";
  pop.hidden = true;
  let pinnedFor = null;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  }

  function fmt(n) {
    if (n === null || n === undefined) return "";
    return n > 0 ? "+" + n : String(n);
  }

  function place(el) {
    pop.hidden = false;
    const r = el.getBoundingClientRect();
    const pw = pop.offsetWidth, ph = pop.offsetHeight;
    let left = r.left + r.width / 2 - pw / 2;
    left = Math.max(8, Math.min(left, window.innerWidth - pw - 8));
    let top = r.bottom + 8;
    if (top + ph > window.innerHeight - 8) top = r.top - ph - 8;
    pop.style.left = left + "px";
    pop.style.top = Math.max(8, top) + "px";
  }

  function showText(el, text) {
    pop.innerHTML = `<div class="tip">${esc(text)}</div>`;
    place(el);
  }

  // Elements whose hover title can also be opened by click (not buttons/links that do something else).
  const TIP_SELECTOR = ".sheet-shell [title], .sheet-shell [data-tip]";
  function tipTarget(target) {
    const el = target.closest(TIP_SELECTOR);
    if (!el || el.closest("a, button, input, select, textarea, label, [hx-post], .play-btn, .modal")) return null;
    const text = el.dataset.tip || el.getAttribute("title");
    return text && text.trim() ? el : null;
  }

  function show(el) {
    let data;
    try { data = JSON.parse(el.dataset.bd); } catch (e) { return; }
    const rows = data.rows.map((r, i) => {
      const label = esc(r[0]);
      const n = r[1] === null ? "" : (i === 0 && data.base ? String(r[1]) : fmt(r[1]));
      return `<tr><td>${label}</td><td class="n">${n}</td></tr>`;
    }).join("");
    const title = el.dataset.title ? `<h4>${esc(el.dataset.title)}</h4>` : "";
    pop.innerHTML = `${title}<table>${rows}<tr class="total"><td>Total</td><td class="n">${data.total}</td></tr></table>`;
    place(el);
  }

  function hide() { pop.hidden = true; pinnedFor = null; pop.classList.remove("pinned"); }

  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");

  document.addEventListener("DOMContentLoaded", () => document.body.appendChild(pop));
  document.addEventListener("mouseover", (e) => {
    if (!finePointer.matches || pinnedFor) return;
    const el = e.target.closest(".has-bd");
    if (el) show(el);
  });
  document.addEventListener("mouseout", (e) => {
    if (!finePointer.matches || pinnedFor) return;
    const el = e.target.closest(".has-bd");
    if (el && !el.contains(e.relatedTarget)) hide();
  });
  document.addEventListener("click", (e) => {
    const el = e.target.closest(".has-bd");
    if (el) {
      e.preventDefault();
      if (pinnedFor === el) { hide(); return; }
      show(el);
      pinnedFor = el;
      pop.classList.add("pinned");
      return;
    }
    const tip = tipTarget(e.target);
    if (tip) {
      if (pinnedFor === tip) { hide(); return; }
      showText(tip, tip.dataset.tip || tip.getAttribute("title"));
      pinnedFor = tip;
      pop.classList.add("pinned");
      return;
    }
    if (!e.target.closest(".bd-pop")) hide();
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });
  window.addEventListener("scroll", () => { if (!pinnedFor) hide(); }, { passive: true });
  document.addEventListener("htmx:beforeSwap", hide);

  // CSRF for htmx requests.
  document.addEventListener("htmx:configRequest", (e) => {
    const token = document.querySelector("meta[name=csrf-token]");
    if (token) e.detail.headers["X-CSRFToken"] = token.content;
  });
})();

/* Alpine component for the sheet: tabs, play panels and specialty details. */
window.sheetUI = function (tab) {
  return {
    tab: tab || "page1",
    panel: null,
    spec: null,
    setTab(t) {
      this.tab = t;
      try { localStorage.setItem("tephra-tab", t); } catch (e) { /* storage unavailable */ }
    },
    openPanel(p) { this.panel = p; },
    close() { this.panel = null; this.spec = null; },
    showSpec(slug) {
      try {
        const data = JSON.parse(document.getElementById("spec-data").textContent);
        this.spec = data[slug] || null;
      } catch (e) { this.spec = null; }
      this.panel = this.spec ? "spec" : null;
    },
  };
};

/* Alpine component for the add-effect form: filterable status list or called-shot location + effect. */
window.effectForm = function () {
  let opts = { status: [], locations: [], called: {} };
  try { opts = JSON.parse(document.getElementById("effect-options").textContent); } catch (e) { /* no data */ }
  return {
    opts, kind: "status", q: "", key: "", open: false, active: 0, location: "", which: "",
    matches() {
      const q = this.q.trim().toLowerCase();
      const list = this.opts.status.filter((o) => !q || o.name.toLowerCase().includes(q));
      if (q && !this.opts.status.some((o) => o.name.toLowerCase() === q)) {
        list.push({ key: "", name: this.q.trim(), text: "custom effect (no automatic changes)" });
      }
      return list;
    },
    move(d) {
      const n = this.matches().length;
      this.open = true;
      if (n) this.active = (this.active + d + n) % n;
    },
    pick(o) {
      if (!o) return;
      this.q = o.name;
      this.key = o.key;
      this.open = false;
    },
    called() { return this.opts.called[this.location] || []; },
    ready() {
      return this.kind === "status" ? !!(this.key || this.q.trim()) : !!(this.location && this.which);
    },
    hint() {
      if (this.kind === "status") {
        const o = this.opts.status.find((s) => s.key === this.key);
        return o ? o.text : "Pick a status effect from the list, or type your own.";
      }
      const c = this.called().find((x) => x.kind === this.which);
      return c ? c.text : "Choose the hit location, then the wounded or fatal effect.";
    },
  };
};
