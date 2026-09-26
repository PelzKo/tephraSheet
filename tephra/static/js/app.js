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
        th.title = th.title || "Sort by this column (click again to reverse)";
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
    status.textContent = "Sending…";
    try {
      const resp = await fetch(form.action, {
        method: "POST", body: data, headers: { "X-CSRFToken": token ? token.content : "" },
      });
      const result = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(result.error || "Could not send feedback.");
      form.querySelector("textarea").value = "";
      status.textContent = "Thanks! Your message was sent to the narrator.";
      setTimeout(() => close(box), 1600);
    } catch (err) {
      status.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  });
})();
