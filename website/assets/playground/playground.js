/* JOBPREP_DA SQL Playground: runs SQLite in the browser (sql.js / WebAssembly). */
(function () {
  "use strict";
  var app = document.getElementById("pg-app");
  if (!app) return;

  var BASE = app.getAttribute("data-base") || ".";
  var VENDOR = app.getAttribute("data-vendor");
  var STORE = "jobprep-sql-v1";
  var MAX_ROWS = 200;
  var state = { db: null, questions: [], current: null, progress: load() };

  function load() {
    try { return JSON.parse(localStorage.getItem(STORE)) || { solved: {}, drafts: {} }; }
    catch (e) { return { solved: {}, drafts: {} }; }
  }
  function save() { try { localStorage.setItem(STORE, JSON.stringify(state.progress)); } catch (e) { /* private mode */ } }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "class") n.className = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }

  function fmt(v) {
    if (v === null || v === undefined) return el("span", { class: "pg-null" }, ["NULL"]);
    if (typeof v === "number") return document.createTextNode(Number.isInteger(v) ? String(v) : v.toLocaleString("en-IN", { maximumFractionDigits: 4 }));
    return document.createTextNode(String(v));
  }

  function table(columns, rows) {
    var t = el("table", { class: "pg-table" });
    var thead = el("thead", {}, [el("tr", {}, columns.map(function (c) { return el("th", {}, [c]); }))]);
    var tbody = el("tbody");
    rows.slice(0, MAX_ROWS).forEach(function (r) {
      tbody.appendChild(el("tr", {}, r.map(function (v) { var td = el("td"); td.appendChild(fmt(v)); return td; })));
    });
    t.appendChild(thead); t.appendChild(tbody);
    var wrap = el("div", { class: "pg-table-wrap" }, [t]);
    if (rows.length > MAX_ROWS) wrap.appendChild(el("p", { class: "pg-muted" }, ["Showing " + MAX_ROWS + " of " + rows.length.toLocaleString() + " rows."]));
    else wrap.appendChild(el("p", { class: "pg-muted" }, [rows.length.toLocaleString() + " row(s)"]));
    return wrap;
  }

  // ------------------------------------------------------------------ layout
  var ui = {};
  function build() {
    app.innerHTML = "";
    ui.select = el("select", { class: "pg-select", "aria-label": "Choose a question", onchange: function () { pick(this.value); } });
    ui.progress = el("span", { class: "pg-progress" });
    ui.prompt = el("div", { class: "pg-prompt" });
    ui.editor = el("textarea", { class: "pg-editor", spellcheck: "false", "aria-label": "SQL editor", rows: "12",
      placeholder: "Write your SQLite query here…  (Ctrl/⌘ + Enter to run)" });
    ui.status = el("div", { class: "pg-status", role: "status", "aria-live": "polite" });
    ui.output = el("div", { class: "pg-output" });
    ui.schema = el("div", { class: "pg-schema" });

    ui.editor.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(false); }
      if (e.key === "Tab" && !e.shiftKey) {
        e.preventDefault();
        var s = this.selectionStart;
        this.value = this.value.slice(0, s) + "    " + this.value.slice(this.selectionEnd);
        this.selectionStart = this.selectionEnd = s + 4;
      }
    });
    ui.editor.addEventListener("input", function () {
      if (state.current) { state.progress.drafts[state.current.id] = ui.editor.value; save(); }
    });

    var buttons = el("div", { class: "pg-buttons" }, [
      el("button", { class: "md-button md-button--primary", onclick: function () { run(false); } }, ["▶ Run"]),
      el("button", { class: "md-button md-button--primary pg-check", onclick: function () { run(true); } }, ["✔ Check answer"]),
      el("button", { class: "md-button", onclick: showSolution }, ["💡 Solution"]),
      el("button", { class: "md-button", onclick: resetEditor }, ["↺ Reset"]),
      el("button", { class: "md-button", onclick: next }, ["Next →"])
    ]);

    var top = el("div", { class: "pg-top" }, [ui.select, ui.progress]);
    var main = el("div", { class: "pg-main" }, [ui.prompt, ui.editor, buttons, ui.status, ui.output]);
    var side = el("aside", { class: "pg-side" }, [el("h3", {}, ["Schema"]), ui.schema,
      el("p", { class: "pg-muted" }, ["Click a table to insert its name. Dialect: SQLite — use strftime() and julianday() for dates."])]);
    app.appendChild(top);
    app.appendChild(el("div", { class: "pg-grid" }, [main, side]));
  }

  function fillSelect() {
    ui.select.innerHTML = "";
    ui.select.appendChild(el("option", { value: "0" }, ["✎ Scratchpad: free queries"]));
    ["Easy", "Medium", "Hard"].forEach(function (lvl) {
      var g = el("optgroup", { label: lvl });
      state.questions.filter(function (q) { return q.level === lvl; }).forEach(function (q) {
        var done = state.progress.solved[q.id] ? "✓ " : "";
        g.appendChild(el("option", { value: String(q.id) }, [done + "Q" + String(q.id).padStart(2, "0") + " · " + q.title]));
      });
      ui.select.appendChild(g);
    });
    var n = Object.keys(state.progress.solved).length;
    ui.progress.textContent = n + " / " + state.questions.length + " solved";
  }

  function fillSchema() {
    var res = state.db.exec("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name");
    ui.schema.innerHTML = "";
    (res[0] ? res[0].values : []).forEach(function (r) {
      var name = r[0];
      var cols = state.db.exec("PRAGMA table_info(" + name + ")")[0].values;
      var count = state.db.exec("SELECT COUNT(*) FROM " + name)[0].values[0][0];
      var det = el("details", {}, [
        el("summary", {}, [el("code", {}, [name]), " ", el("span", { class: "pg-muted" }, [count.toLocaleString() + " rows"])]),
        el("ul", {}, cols.map(function (c) { return el("li", {}, [el("code", {}, [c[1]]), " ", el("span", { class: "pg-muted" }, [c[2] || ""])]); }))
      ]);
      det.querySelector("summary").addEventListener("dblclick", function () { insert(name); });
      det.querySelector("code").addEventListener("click", function (e) { e.preventDefault(); insert(name); });
      ui.schema.appendChild(det);
    });
  }

  function insert(text) {
    var ed = ui.editor, s = ed.selectionStart;
    ed.value = ed.value.slice(0, s) + text + ed.value.slice(ed.selectionEnd);
    ed.focus(); ed.selectionStart = ed.selectionEnd = s + text.length;
    ed.dispatchEvent(new Event("input"));
  }

  // ------------------------------------------------------------------ actions
  function pick(id) {
    id = Number(id);
    state.current = state.questions.find(function (q) { return q.id === id; }) || null;
    ui.status.className = "pg-status"; ui.status.textContent = ""; ui.output.innerHTML = "";
    if (!state.current) {
      ui.prompt.innerHTML = "<h2>Scratchpad</h2><p>Run any query against the ShopKart database. Try: " +
        "<code>SELECT * FROM orders LIMIT 10;</code></p>";
      ui.editor.value = state.progress.drafts[0] || "SELECT * FROM orders LIMIT 10;";
      document.querySelector(".pg-check").disabled = true;
    } else {
      var q = state.current;
      ui.prompt.innerHTML = "";
      ui.prompt.appendChild(el("div", { class: "pg-badges" }, [
        el("span", { class: "pg-badge pg-" + q.level.toLowerCase() }, [q.level]),
        el("span", { class: "pg-muted" }, [q.topics]),
        state.progress.solved[q.id] ? el("span", { class: "pg-badge pg-solved" }, ["✓ solved"]) : el("span")
      ]));
      ui.prompt.appendChild(el("h2", {}, ["Q" + String(q.id).padStart(2, "0") + " · " + q.title]));
      ui.prompt.appendChild(el("div", { html: q.prompt_html }));
      ui.prompt.appendChild(el("p", { class: "pg-muted" }, [
        "Expected columns: " + q.expected.columns.join(", ") + " · " + q.expected.rows.length + " row(s) · " +
        (q.ordered ? "row order matters" : "any row order")]));
      ui.editor.value = state.progress.drafts[q.id] || "-- Q" + String(q.id).padStart(2, "0") + ": " + q.title + "\n";
      document.querySelector(".pg-check").disabled = false;
    }
    ui.select.value = String(id);
    try { history.replaceState(null, "", "#q" + id); } catch (e) { /* file:// */ }
  }

  function run(check) {
    ui.output.innerHTML = ""; ui.status.className = "pg-status";
    var sql = ui.editor.value.trim();
    if (!sql) { ui.status.textContent = "Write a query first."; return; }
    var t0 = performance.now(), result;
    try { result = JobprepGrader.runSql(state.db, sql); }
    catch (err) {
      ui.status.className = "pg-status pg-bad";
      ui.status.textContent = "SQL error: " + err.message;
      return;
    }
    var ms = Math.round(performance.now() - t0);
    if (!check || !state.current) {
      ui.status.textContent = "Ran in " + ms + " ms." + (state.current ? "  Click “Check answer” to grade it." : "");
      if (result.columns.length) ui.output.appendChild(table(result.columns, result.values));
      return;
    }
    var q = state.current, verdict = JobprepGrader.grade(result, q.expected, q.ordered);
    ui.status.className = "pg-status " + (verdict.ok ? "pg-good" : "pg-bad");
    ui.status.textContent = (verdict.ok ? "✅ " : "❌ ") + verdict.reason;
    if (verdict.ok) {
      state.progress.solved[q.id] = true; save(); fillSelect(); ui.select.value = String(q.id);
    }
    ui.output.appendChild(el("h4", {}, ["Your result"]));
    ui.output.appendChild(table(result.columns, result.values));
    if (!verdict.ok) {
      ui.output.appendChild(el("h4", {}, ["Expected (first rows)"]));
      ui.output.appendChild(table(q.expected.columns, q.expected.rows.slice(0, 8)));
    }
  }

  function showSolution() {
    if (!state.current) return;
    if (!confirm("Show the reference solution? Try for a few more minutes first!")) return;
    ui.output.innerHTML = "";
    ui.output.appendChild(el("h4", {}, ["Reference solution"]));
    ui.output.appendChild(el("pre", { class: "pg-solution" }, [el("code", {}, [state.current.solution])]));
    var b = el("button", { class: "md-button", onclick: function () { ui.editor.value = state.current.solution; ui.editor.dispatchEvent(new Event("input")); } }, ["Copy into editor"]);
    ui.output.appendChild(b);
  }

  function resetEditor() {
    if (!confirm("Clear your query for this question?")) return;
    var id = state.current ? state.current.id : 0;
    delete state.progress.drafts[id]; save(); pick(id);
  }

  function next() {
    var id = state.current ? state.current.id : 0;
    var nxt = state.questions.find(function (q) { return q.id > id; });
    pick(nxt ? nxt.id : 0);
  }

  // ------------------------------------------------------------------ boot
  build();
  ui.status.textContent = "Loading SQLite (WebAssembly) and the ShopKart database…";
  Promise.all([
    initSqlJs({ locateFile: function (f) { return VENDOR + "/" + f; } }),
    fetch(BASE + "/shopkart.db").then(function (r) { if (!r.ok) throw new Error("database " + r.status); return r.arrayBuffer(); }),
    fetch(BASE + "/questions.json").then(function (r) { if (!r.ok) throw new Error("questions " + r.status); return r.json(); })
  ]).then(function (res) {
    state.db = new res[0].Database(new Uint8Array(res[1]));
    state.questions = res[2];
    fillSelect(); fillSchema();
    var m = /#q(\d+)/.exec(location.hash);
    pick(m ? Number(m[1]) : 1);
  }).catch(function (err) {
    ui.status.className = "pg-status pg-bad";
    ui.status.textContent = "Could not load the playground: " + err.message +
      ". If you opened this file directly from disk, serve the site over HTTP instead (mkdocs serve).";
  });
})();
