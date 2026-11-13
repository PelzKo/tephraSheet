/* Breakdown popovers for composite values: hover on mouse devices, click/tap everywhere.
   Any other sheet element with a hover title (truncated text, racial traits, locations) shows
   that text in the same popover on click/tap, so everything works on tablets too. */
/* UI texts: the page embeds {English: translation} for exactly the strings below (js_i18n). */
const t = (function () {
  let dict = {};
  try { dict = JSON.parse(document.getElementById("js-i18n").textContent) || {}; } catch (e) { /* no dict */ }
  return (s) => dict[s] || s;
})();

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
    pop.innerHTML = `${title}<table>${rows}<tr class="total"><td>${esc(t("Total"))}</td><td class="n">${data.total}</td></tr></table>`;
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
    qty: null,
    init() {
      // An action from inside a panel keeps it open across the swap (state saved in htmx:beforeSwap).
      const keep = window.tephraKeep;
      window.tephraKeep = null;
      if (!keep) return;
      if (keep.spec) this.showSpec(keep.spec);
      else if (keep.panel) this.panel = keep.panel;
    },
    // Wound message button: open the Health panel with the called-shot form preset (effectForm.preset).
    addCalled(which) {
      this.panel = "health";
      this.$nextTick(() => window.dispatchEvent(new CustomEvent("preset-called", { detail: which })));
    },
    // "2 AP", "1 AP, Stance" → 2 / 1; 0 if the cost states no AP.
    apCost(spec) {
      const m = /(\d+)\s*AP/.exec((spec && spec.cost) || "");
      return m ? +m[1] : 0;
    },
    openQty(ev, id, n, name, removeText) {
      const r = ev.currentTarget.getBoundingClientRect();
      this.qty = { id, n, name, removeText, x: Math.max(8, Math.min(r.left, window.innerWidth - 260)), y: r.bottom + 4 };
    },
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
    opts, kind: "status", q: "", key: "", open: false, active: 0, location: "", which: "", want: "",
    preset(which) { this.kind = "called"; this.location = ""; this.which = ""; this.want = which; },
    located() { if (this.want) this.$nextTick(() => { this.which = this.want; }); },
    matches() {
      const q = this.q.trim().toLowerCase();
      const list = this.opts.status.filter((o) => !q || o.name.toLowerCase().includes(q));
      if (q && !this.opts.status.some((o) => o.name.toLowerCase() === q)) {
        list.push({ key: "", name: this.q.trim(), text: t("custom effect (no automatic changes)") });
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
        return o ? o.text : t("Pick a status effect from the list, or type your own.");
      }
      const c = this.called().find((x) => x.kind === this.which);
      return c ? c.text : t("Choose the hit location, then the wounded or fatal effect.");
    },
  };
};

/* Sortable tables: click (or Enter on) a header of any table.data to sort by that column, click again
   to reverse. A cell's data-sort overrides its text (size rank, price in dukes). Empty values always go
   last. Headers marked data-nosort (action columns) stay inert. The chosen order survives htmx swaps,
   e.g. when the catalog filter re-renders its results. */
(function () {
  const chosen = {};  // table key -> {col, dir}
  const NUM = /^[+\-−]?\d+(?:[.,]\d+)?$/;
  const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });

  function headerRow(table) { return Array.from(table.rows).find((r) => r.querySelector("th")); }

  function tableKey(table) {
    const all = Array.from(document.querySelectorAll("table.data"));
    return location.pathname + "#" + all.indexOf(table);
  }

  function cellValue(row, col) {
    const cell = row.cells[col];
    if (!cell) return "";
    return (cell.dataset.sort !== undefined ? cell.dataset.sort : cell.textContent).trim();
  }

  function compare(a, b) {
    if (a === "" || b === "") return a === b ? 0 : (a === "" ? 1 : -1);
    if (NUM.test(a) && NUM.test(b)) {
      const n = (s) => parseFloat(s.replace("−", "-").replace(",", "."));
      return n(a) - n(b);
    }
    return collator.compare(a, b);
  }

  function sortTable(table, col, dir) {
    const head = headerRow(table);
    if (!head || !head.cells[col]) return;
    const rows = Array.from(table.rows).filter((r) => r !== head && !r.hasAttribute("data-nosort"));
    if (!rows.length) return;
    const parent = rows[0].parentNode;
    rows
      .map((r, i) => ({ r, i, v: cellValue(r, col) }))
      .sort((x, y) => {
        if (x.v === "" || y.v === "") return compare(x.v, y.v) || x.i - y.i;  // empties last both ways
        return dir * compare(x.v, y.v) || x.i - y.i;
      })
      .forEach((x) => parent.appendChild(x.r));
    Array.from(head.cells).forEach((th, i) => {
      th.classList.toggle("sorted-asc", i === col && dir > 0);
      th.classList.toggle("sorted-desc", i === col && dir < 0);
      if (th.classList.contains("sortable")) th.setAttribute("aria-sort", i === col ? (dir > 0 ? "ascending" : "descending") : "none");
    });
  }

  function prepare(root) {
    (root.querySelectorAll ? root : document).querySelectorAll("table.data").forEach((table) => {
      const head = headerRow(table);
      if (!head) return;
      Array.from(head.cells).forEach((th) => {
        if (th.tagName !== "TH" || th.hasAttribute("data-nosort") || !th.textContent.trim()) return;
        th.classList.add("sortable");
        th.tabIndex = 0;
        th.title = th.title || t("Sort by this column (click again to reverse)");
      });
      const saved = chosen[tableKey(table)];
      if (saved) sortTable(table, saved.col, saved.dir);
    });
  }

  function activate(th) {
    const table = th.closest("table");
    const col = Array.from(th.parentNode.cells).indexOf(th);
    const key = tableKey(table);
    const prev = chosen[key];
    const dir = prev && prev.col === col ? -prev.dir : 1;
    chosen[key] = { col, dir };
    sortTable(table, col, dir);
  }

  document.addEventListener("click", (e) => {
    const th = e.target.closest("table.data th.sortable");
    if (th) activate(th);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const th = e.target.closest && e.target.closest("table.data th.sortable");
    if (th) { e.preventDefault(); activate(th); }
  });
  document.addEventListener("DOMContentLoaded", () => prepare(document));
  document.addEventListener("htmx:afterSettle", (e) => prepare(e.target));
})();

/* Inventory toolbar: search, kind filter and sort order for the inventory list. Works on the rendered
   rows (data-* attributes), remembers the choice per character in localStorage and re-applies it after
   every htmx re-render of the sheet. */
(function () {
  const rank = (s, empty) => (s === "" || s === undefined ? empty : +s);  // sizeless items last
  const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });
  const SORTS = {
    slot: (a, b) => a.dataset.idx - b.dataset.idx,
    "name-asc": (a, b) => collator.compare(a.dataset.name, b.dataset.name),
    "name-desc": (a, b) => collator.compare(b.dataset.name, a.dataset.name),
    "price-desc": (a, b) => b.dataset.price - a.dataset.price,
    "price-asc": (a, b) => a.dataset.price - b.dataset.price,
    "value-desc": (a, b) => b.dataset.price * b.dataset.qty - a.dataset.price * a.dataset.qty,
    "size-desc": (a, b) => rank(b.dataset.size, -1) - rank(a.dataset.size, -1),
    "size-asc": (a, b) => rank(a.dataset.size, 99) - rank(b.dataset.size, 99),
    kind: (a, b) => collator.compare(a.dataset.kindLabel, b.dataset.kindLabel),
  };

  function storageKey(bar) { return "tephra-inv-" + bar.dataset.character; }

  function load(bar) {
    try { return JSON.parse(localStorage.getItem(storageKey(bar))) || {}; } catch (e) { return {}; }
  }

  function save(bar, state) {
    try { localStorage.setItem(storageKey(bar), JSON.stringify(state)); } catch (e) { /* storage unavailable */ }
  }

  function apply(bar) {
    const list = document.querySelector(bar.dataset.target);
    if (!list) return;
    const q = bar.querySelector("[data-inv-q]").value.trim().toLowerCase();
    const kind = bar.querySelector("[data-inv-kind]").value;
    const sort = bar.querySelector("[data-inv-sort]").value;
    const rows = Array.from(list.querySelectorAll(":scope > [data-idx]"));
    let shown = 0;
    rows.forEach((r) => {
      const ok = (!q || r.dataset.text.includes(q)) && (!kind || r.dataset.kind === kind);
      r.hidden = !ok;
      if (ok) shown += 1;
    });
    const cmp = SORTS[sort] || SORTS.slot;
    rows.sort((a, b) => cmp(a, b) || a.dataset.idx - b.dataset.idx).forEach((r) => list.appendChild(r));
    const empty = list.querySelector("[data-inv-empty]");
    if (empty) {
      empty.hidden = !(rows.length && !shown);
      list.appendChild(empty);
    }
    save(bar, { q: bar.querySelector("[data-inv-q]").value, kind, sort });
  }

  function init(root) {
    (root.querySelectorAll ? root : document).querySelectorAll("[data-inv-toolbar]").forEach((bar) => {
      const state = load(bar);
      bar.querySelector("[data-inv-q]").value = state.q || "";
      const kindSel = bar.querySelector("[data-inv-kind]");
      kindSel.value = state.kind || "";
      if (kindSel.value !== (state.kind || "")) kindSel.value = "";  // kind no longer in the inventory
      const sortSel = bar.querySelector("[data-inv-sort]");
      sortSel.value = state.sort || "slot";
      if (!sortSel.value) sortSel.value = "slot";
      apply(bar);
    });
  }

  document.addEventListener("input", (e) => {
    const bar = e.target.closest && e.target.closest("[data-inv-toolbar]");
    if (bar) apply(bar);
  });
  document.addEventListener("change", (e) => {
    const bar = e.target.closest && e.target.closest("[data-inv-toolbar]");
    if (bar) apply(bar);
  });
  document.addEventListener("click", (e) => {
    const reset = e.target.closest("[data-inv-reset]");
    if (!reset) return;
    const bar = reset.closest("[data-inv-toolbar]");
    bar.querySelector("[data-inv-q]").value = "";
    bar.querySelector("[data-inv-kind]").value = "";
    bar.querySelector("[data-inv-sort]").value = "slot";
    apply(bar);
  });
  document.addEventListener("DOMContentLoaded", () => init(document));
  document.addEventListener("htmx:afterSettle", (e) => init(e.target));
})();

/* Feedback bubble: a floating button on every page opens a small form (bug / feature / feedback).
   Along with the text it sends where the user was: page, character, sheet tab and device details. */
(function () {
  function meta(box) {
    const sheet = document.getElementById("sheet-body");
    let tab = "";
    try { if (sheet && window.Alpine) tab = Alpine.$data(sheet).tab || ""; } catch (e) { /* no sheet */ }
    return {
      tab,
      viewport: `${window.innerWidth}×${window.innerHeight}`,
      screen: `${screen.width}×${screen.height} @${window.devicePixelRatio || 1}x`,
      orientation: window.matchMedia("(orientation: portrait)").matches ? "portrait" : "landscape",
      touch: window.matchMedia("(pointer: coarse)").matches,
      language: navigator.language || "",
      timezone: (Intl.DateTimeFormat().resolvedOptions() || {}).timeZone || "",
      local_time: new Date().toString(),
      referrer: document.referrer || "",
      admin_mode: !!document.querySelector(".admin-banner"),
      scroll_y: Math.round(window.scrollY),
    };
  }

  function open(box) {
    box.hidden = false;
    box.querySelector("[data-fb-status]").textContent = "";
    box.querySelector("textarea").focus();
  }

  function close(box) { box.hidden = true; }

  document.addEventListener("click", (e) => {
    const box = document.querySelector("[data-fb]");
    if (!box) return;
    if (e.target.closest("[data-fb-open]")) { open(box); return; }
    if (e.target.closest("[data-fb-close]") || e.target === box) close(box);
  });
  document.addEventListener("keydown", (e) => {
    const box = document.querySelector("[data-fb]");
    if (e.key === "Escape" && box && !box.hidden) close(box);
  });
  document.addEventListener("submit", async (e) => {
    const form = e.target.closest("[data-fb-form]");
    if (!form) return;
    e.preventDefault();
    const box = form.closest("[data-fb]");
    const status = form.querySelector("[data-fb-status]");
    const button = form.querySelector("button[type=submit]");
    const data = new FormData(form);
    data.set("page_url", location.href);
    data.set("page_title", document.title);
    data.set("meta", JSON.stringify(meta(box)));
    const token = document.querySelector("meta[name=csrf-token]");
    button.disabled = true;
    status.textContent = t("Sending…");
    try {
      const resp = await fetch(form.action, {
        method: "POST", body: data, headers: { "X-CSRFToken": token ? token.content : "" },
      });
      const result = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(result.error || t("Could not send feedback."));
      form.querySelector("textarea").value = "";
      status.textContent = t("Thanks! Your message was sent to the narrator.");
      setTimeout(() => close(box), 1600);
    } catch (err) {
      status.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  });
})();

/* Sheet robustness (all keyed to #sheet-body, which every play action replaces):
   - drafts: [data-draft] fields are saved to localStorage while typing and put back after a swap or reload;
     cleared when the server accepted the save. [data-draft-base] carries the edit-conflict stamp along.
   - failed requests show a "Not saved – tap to retry" bar (hx-sync="this:drop" on #sheet-body stops double taps).
   - open panel, open companion <details> and the last-used input survive the swap.
   - live refresh: polls the character's stamp and re-fetches the sheet when another device changed it.
   - money panel asks before a balance goes negative; offline note; pencil print; service worker. */
(function () {
  const body = () => document.getElementById("sheet-body");
  const draftKey = (el) => { const b = body(); return b ? `tephra-draft-${b.dataset.character}-${el.dataset.draft}` : null; };
  const load = (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
  const store = (k, v) => { try { v ? localStorage.setItem(k, JSON.stringify(v)) : localStorage.removeItem(k); } catch (e) { /* no storage */ } };
  const baseOf = (el) => el.form && el.form.querySelector("[data-draft-base]");

  function hasDrafts() {
    const b = body();
    if (!b) return false;
    try {
      const prefix = `tephra-draft-${b.dataset.character}-`;
      for (let i = 0; i < localStorage.length; i++) if (localStorage.key(i).startsWith(prefix)) return true;
    } catch (e) { /* no storage */ }
    return false;
  }

  document.addEventListener("input", (e) => {
    const el = e.target.closest && e.target.closest("[data-draft]");
    const k = el && draftKey(el);
    if (!k) return;
    const old = load(k);
    const base = baseOf(el);
    store(k, el.value === el.defaultValue ? null : { text: el.value, base: old ? old.base : (base ? base.value : "") });
  });

  function restore() {
    document.querySelectorAll("#sheet-body [data-draft]").forEach((el) => {
      const k = draftKey(el);
      const d = load(k);
      const base = baseOf(el);
      if (el.form && el.form.querySelector("[data-conflict]")) {
        // Edit conflict: the editor shows the user's text; keep it as a draft against the new stamp.
        store(k, { text: el.value, base: base ? base.value : "" });
        return;
      }
      if (!d) return;
      if (d.text === el.defaultValue) { store(k, null); return; }
      el.value = d.text;
      el.setAttribute("data-draft-restored", "");
      if (base && d.base) base.value = d.base;
      try { const scope = window.Alpine && Alpine.$data(el); if (scope && "edit" in scope) scope.edit = true; } catch (err) { /* not initialised yet: x-init does it */ }
    });
  }

  // --- error bar ---------------------------------------------------------------------------------
  let failed = null;
  const bar = document.createElement("button");
  bar.type = "button";
  bar.className = "net-error";
  bar.hidden = true;
  bar.addEventListener("click", () => {
    const f = failed;
    bar.hidden = true;
    failed = null;
    if (f && f.elt.isConnected) htmx.ajax(f.verb, f.path, { source: f.elt, target: "#sheet-body", swap: "outerHTML", values: f.values });
  });
  const offline = document.createElement("div");
  offline.className = "net-offline";
  offline.hidden = navigator.onLine;
  const showOffline = () => { offline.hidden = navigator.onLine; };
  window.addEventListener("online", showOffline);
  window.addEventListener("offline", showOffline);

  function onFail(e) {
    const cfg = e.detail.requestConfig;
    if (!cfg || cfg.verb === "get") return;  // searches/refreshes: nothing was lost
    const values = {};
    if (cfg.formData) for (const [k, v] of cfg.formData.entries()) values[k] = k in values ? [].concat(values[k], v) : v;
    failed = { verb: cfg.verb, path: cfg.path, elt: cfg.elt, values };
    bar.textContent = t("Not saved – tap to retry");
    bar.hidden = false;
  }
  document.addEventListener("htmx:responseError", onFail);
  document.addEventListener("htmx:sendError", onFail);
  document.addEventListener("htmx:afterRequest", (e) => { if (e.detail.successful && e.detail.requestConfig && e.detail.requestConfig.verb !== "get") bar.hidden = true; });

  // --- state across swaps ---------------------------------------------------------------------------
  let lastInput = null;
  document.addEventListener("focusin", (e) => {
    if (e.target.matches && e.target.matches("#sheet-body input[type=number], #sheet-body input[type=text]")) lastInput = e.target;
  });
  let refocus = null;
  let keptDetails = [];

  document.addEventListener("htmx:beforeSwap", (e) => {
    const b = body();
    if (!b || e.detail.target !== b || !e.detail.shouldSwap) return;
    const elt = e.detail.requestConfig && e.detail.requestConfig.elt;
    // The server took the save (no conflict box in the answer): forget the drafts of that form.
    if (elt && elt.querySelectorAll && !String(e.detail.serverResponse).includes("data-conflict")) {
      elt.querySelectorAll("[data-draft]").forEach((el) => store(draftKey(el), null));
    }
    keptDetails = [...b.querySelectorAll("details[data-keep][open]")].map((d) => d.dataset.keep);
    const keep = {};
    try {
      const ui = Alpine.$data(b);
      keep.panel = ui.panel;
      keep.spec = ui.panel === "spec" && ui.spec ? ui.spec.slug : null;
    } catch (err) { /* Alpine not ready */ }
    window.tephraKeep = keep;
    refocus = null;
    if (lastInput && lastInput.isConnected && elt && elt.contains && elt.contains(lastInput) && lastInput.form) {
      const post = lastInput.form.getAttribute("hx-post");
      const forms = [...b.querySelectorAll("form")].filter((f) => f.getAttribute("hx-post") === post);
      refocus = { post, idx: forms.indexOf(lastInput.form), name: lastInput.name };
    }
  });

  document.addEventListener("htmx:afterSettle", () => {
    const b = body();
    if (!b) return;
    restore();
    keptDetails.forEach((k) => { const d = b.querySelector(`details[data-keep="${CSS.escape(k)}"]`); if (d) d.open = true; });
    keptDetails = [];
    if (refocus) {
      const form = [...b.querySelectorAll("form")].filter((f) => f.getAttribute("hx-post") === refocus.post)[refocus.idx];
      const input = form && form.querySelector(`[name="${CSS.escape(refocus.name)}"]`);
      if (input && input.offsetParent !== null) input.focus({ preventScroll: true });
      refocus = null;
    }
  });

  // --- live refresh -------------------------------------------------------------------------------
  function busy(b) {
    if (b.querySelector(".htmx-request") || b.classList.contains("htmx-request") || b.hasAttribute("data-autoprint")) return true;
    const a = document.activeElement;
    if (a && b.contains(a) && a.matches("input, textarea, select")) return true;
    if (hasDrafts()) return true;
    try { const ui = Alpine.$data(b); if (ui.panel || ui.qty) return true; } catch (e) { return true; }
    return [...b.querySelectorAll(".modal-backdrop")].some((m) => getComputedStyle(m).display !== "none");
  }
  async function poll() {
    const b = body();
    if (!b || document.hidden || !navigator.onLine || busy(b)) return;
    try {
      const resp = await fetch(b.dataset.stampUrl, { headers: { Accept: "application/json" }, credentials: "same-origin" });
      if (!resp.ok || !(resp.headers.get("content-type") || "").includes("json")) return;
      const data = await resp.json();
      const now = body();
      if (now && data.stamp !== now.dataset.stamp && !busy(now)) {
        let tab = "page1";
        try { tab = Alpine.$data(now).tab; } catch (e) { /* default */ }
        htmx.ajax("GET", `${now.dataset.sheetUrl}?tab=${encodeURIComponent(tab)}`, { source: now, target: "#sheet-body", swap: "outerHTML" });
      }
    } catch (e) { /* offline: try again later */ }
  }

  // --- money: ask before a balance goes negative ----------------------------------------------------
  document.addEventListener("htmx:confirm", (e) => {
    const f = e.detail.elt;
    if (!f.matches || !f.matches("form[data-money]")) return;
    const ev = e.detail.triggeringEvent;
    const op = ev && ev.submitter ? ev.submitter.value : "gain";
    const amount = (+f.elements.amount.value || 0) * ({ k: 100, pr: 10, d: 1 }[f.elements.unit.value] || 1);
    const hand = +f.dataset.hand, bank = +f.dataset.bank, inBank = f.elements.where.value === "bank";
    const negative = (op === "spend" && (inBank ? bank : hand) - amount < 0) ||
      (op === "to_bank" && hand - amount < 0) || (op === "to_hand" && bank - amount < 0);
    if (!negative) return;
    e.preventDefault();
    if (window.confirm(t("This makes the balance negative. Continue?"))) e.detail.issueRequest(true);
  });

  // Info icons next to play-bar chips: keyboard opens them like a tap.
  document.addEventListener("keydown", (e) => {
    if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches(".info-tip")) { e.preventDefault(); e.target.click(); }
  });
  // Print: companion details open in the appendix.
  window.addEventListener("beforeprint", () => document.querySelectorAll(".print-appendix details").forEach((d) => { d.open = true; }));

  function start() {
    document.body.appendChild(bar);
    offline.textContent = t("Offline – read only");
    document.body.appendChild(offline);
    const b = body();
    if (!b) return;
    restore();
    setInterval(poll, 5000);
    if (b.hasAttribute("data-autoprint")) window.addEventListener("load", () => setTimeout(() => window.print(), 300));
    if ("serviceWorker" in navigator && b.dataset.sw) navigator.serviceWorker.register(b.dataset.sw).catch(() => { /* optional */ });
  }
  // Deferred script: the DOM is parsed and Alpine (loaded after this file) has not started yet, so the
  // journal's x-init already sees restored drafts.
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
