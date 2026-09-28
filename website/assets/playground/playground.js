/* JOBPREP_DA SQL Playground: runs SQLite in the browser (sql.js / WebAssembly).
 * Two question sets: the practice questions (#q1, #q2, …) and the timed mock live-SQL rounds (#m1, #m2, … numbered
 * globally across rounds; each mock question carries `round`, `round_name` and its number within the round, `num`). */
(function () {
  "use strict";
  var app = document.getElementById("pg-app");
  if (!app) return;

  var BASE = app.getAttribute("data-base") || ".";
  var VENDOR = app.getAttribute("data-vendor");
  var STORE = "jobprep-sql-v1";
  var MAX_ROWS = 200;
  var MOCK_MINUTES = 45;
  var state = { db: null, questions: [], mock: [], current: null, hintsShown: 0, timer: null, progress: load() };

  function load() {
    var blank = { solved: {}, drafts: {}, mockHistory: [] };
    try { return Object.assign(blank, JSON.parse(localStorage.getItem(STORE)) || {}); }
    catch (e) { return blank; }
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
  function mmss(sec) { sec = Math.max(0, Math.round(sec)); return Math.floor(sec / 60) + ":" + String(sec % 60).padStart(2, "0"); }
  function isMock(q) { return q && String(q.id).charAt(0) === "m"; }
  function label(q) {
    if (!isMock(q)) return "Q" + String(q.id).padStart(2, "0");
    return q.round ? "R" + q.round + "·Q" + q.num : "M" + q.id.slice(1);
  }
  function rounds() {
    var seen = {}, out = [];
    state.mock.forEach(function (q) { var r = q.round || 1; if (!seen[r]) { seen[r] = true; out.push({ round: r, name: q.round_name || "Live SQL round" }); } });
    return out;
  }
  function roundQs(r) { return state.mock.filter(function (q) { return (q.round || 1) === r; }); }
  function range(qs) { return label(qs[0]) + "–" + label(qs[qs.length - 1]); }

  function table(columns, rows) {
    var t = el("table", { class: "pg-table" });
    t.appendChild(el("thead", {}, [el("tr", {}, columns.map(function (c) { return el("th", {}, [c]); }))]));
    var tbody = el("tbody");
    rows.slice(0, MAX_ROWS).forEach(function (r) {
      tbody.appendChild(el("tr", {}, r.map(function (v) { var td = el("td"); td.appendChild(fmt(v)); return td; })));
    });
    t.appendChild(tbody);
    var wrap = el("div", { class: "pg-table-wrap" }, [t]);
    wrap.appendChild(el("p", { class: "pg-muted" }, [rows.length > MAX_ROWS
      ? "Showing " + MAX_ROWS + " of " + rows.length.toLocaleString() + " rows."
      : rows.length.toLocaleString() + " row(s)"]));
    return wrap;
  }

  // ------------------------------------------------------------------ layout
  var ui = {};
  function build() {
    app.innerHTML = "";
    ui.select = el("select", { class: "pg-select", "aria-label": "Choose a question", onchange: function () { pick(this.value); } });
    ui.progress = el("span", { class: "pg-progress" });
    ui.roundSel = el("select", { class: "pg-select pg-round-select", "aria-label": "Mock interview round" });
    ui.timerBtn = el("button", { class: "md-button pg-timer-btn", onclick: toggleMock }, ["⏱ Start timed mock (45 min)"]);
    ui.clock = el("span", { class: "pg-clock", "aria-live": "off" });
    ui.prompt = el("div", { class: "pg-prompt" });
    ui.editor = el("textarea", { class: "pg-editor", spellcheck: "false", "aria-label": "SQL editor", rows: "12",
      placeholder: "Write your SQLite query here…  (Ctrl/⌘ + Enter to run)" });
    ui.hints = el("div", { class: "pg-hints" });
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
      state.progress.drafts[state.current ? state.current.id : 0] = ui.editor.value; save();
    });

    ui.checkBtn = el("button", { class: "md-button md-button--primary", onclick: function () { run(true); } }, ["✔ Check answer"]);
    ui.hintBtn = el("button", { class: "md-button", onclick: showHint }, ["💡 Hint"]);
    var buttons = el("div", { class: "pg-buttons" }, [
      el("button", { class: "md-button md-button--primary", onclick: function () { run(false); } }, ["▶ Run"]),
      ui.checkBtn, ui.hintBtn,
      el("button", { class: "md-button", onclick: showSolution }, ["🔑 Solution"]),
      el("button", { class: "md-button", onclick: resetEditor }, ["↺ Reset"]),
      el("button", { class: "md-button", onclick: next }, ["Next →"])
    ]);

    var top = el("div", { class: "pg-top" }, [ui.select, ui.progress, ui.roundSel, ui.timerBtn, ui.clock]);
    var main = el("div", { class: "pg-main" }, [ui.prompt, ui.editor, buttons, ui.hints, ui.status, ui.output]);
    var side = el("aside", { class: "pg-side" }, [el("h3", {}, ["Schema"]), ui.schema,
      el("p", { class: "pg-muted" }, ["Click a table to insert its name. Dialect: SQLite — use strftime() and julianday() for dates."])]);
    app.appendChild(top);
    app.appendChild(el("div", { class: "pg-grid" }, [main, side]));
  }

  function fillSelect() {
    var keep = ui.select.value;
    ui.select.innerHTML = "";
    ui.select.appendChild(el("option", { value: "0" }, ["✎ Scratchpad: free queries"]));
    ["Easy", "Medium", "Hard"].forEach(function (lvl) {
      var g = el("optgroup", { label: lvl });
      state.questions.filter(function (q) { return q.level === lvl; }).forEach(function (q) {
        g.appendChild(el("option", { value: String(q.id) }, [(state.progress.solved[q.id] ? "✓ " : "") + label(q) + " · " + q.title]));
      });
      ui.select.appendChild(g);
    });
    rounds().forEach(function (r) {
      var g = el("optgroup", { label: "🎤 Mock interview: " + r.name });
      roundQs(r.round).forEach(function (q) {
        g.appendChild(el("option", { value: q.id }, [(state.progress.solved[q.id] ? "✓ " : "") + label(q) + " · " + q.title + " (≈" + q.minutes + " min)"]));
      });
      ui.select.appendChild(g);
    });
    var n = state.questions.filter(function (q) { return state.progress.solved[q.id]; }).length;
    ui.progress.textContent = n + " / " + state.questions.length + " solved";
    if (keep) ui.select.value = keep;
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

  function find(id) {
    id = String(id);
    return state.questions.concat(state.mock).find(function (q) { return String(q.id) === id; }) || null;
  }

  // ------------------------------------------------------------------ actions
  function pick(id) {
    state.current = find(id);
    state.hintsShown = 0;
    ui.status.className = "pg-status"; ui.status.textContent = ""; ui.output.innerHTML = ""; ui.hints.innerHTML = "";
    var q = state.current;
    if (!q) {
      ui.prompt.innerHTML = "<h2>Scratchpad</h2><p>Run any query against the ShopKart database. Try: " +
        "<code>SELECT * FROM orders LIMIT 10;</code></p>";
      ui.editor.value = state.progress.drafts[0] || "SELECT * FROM orders LIMIT 10;";
    } else {
      ui.prompt.innerHTML = "";
      ui.prompt.appendChild(el("div", { class: "pg-badges" }, [
        el("span", { class: "pg-badge pg-" + q.level.toLowerCase() }, [isMock(q) ? "Mock interview" : q.level]),
        el("span", { class: "pg-muted" }, [q.topics]),
        state.progress.solved[q.id] ? el("span", { class: "pg-badge pg-solved" }, ["✓ solved"]) : el("span")
      ]));
      ui.prompt.appendChild(el("h2", {}, [label(q) + " · " + q.title]));
      if (isMock(q)) ui.prompt.appendChild(el("p", { class: "pg-muted" }, ["🎤 The interviewer says:"]));
      ui.prompt.appendChild(el("div", { class: isMock(q) ? "pg-quote" : "", html: q.prompt_html }));
      ui.prompt.appendChild(el("p", { class: "pg-muted" }, [isMock(q)
        ? "Like a real interview, the expected columns aren't given: decide them yourself (the column COUNT is graded, names aren't). Any row order."
        : "Expected columns: " + q.expected.columns.join(", ") + " · " + q.expected.rows.length + " row(s) · " +
          (q.ordered ? "row order matters" : "any row order")]));
      ui.editor.value = state.progress.drafts[q.id] || "-- " + label(q) + ": " + q.title + "\n";
    }
    ui.checkBtn.disabled = !q;
    ui.hintBtn.disabled = !(q && q.hints && q.hints.length);
    ui.hintBtn.textContent = q && q.hints && q.hints.length ? "💡 Hint (" + q.hints.length + ")" : "💡 Hint";
    ui.select.value = q ? String(q.id) : "0";
    if (isMock(q) && !state.timer) ui.roundSel.value = String(q.round || 1);
    try { history.replaceState(null, "", q ? (isMock(q) ? "#" + q.id : "#q" + q.id) : "#scratch"); } catch (e) { /* file:// */ }
  }

  function showHint() {
    var q = state.current;
    if (!q || !q.hints || state.hintsShown >= q.hints.length) return;
    ui.hints.appendChild(el("div", { class: "pg-hint", html: "<b>Hint " + (state.hintsShown + 1) + ":</b> " + q.hints[state.hintsShown] }));
    state.hintsShown++;
    var left = q.hints.length - state.hintsShown;
    ui.hintBtn.textContent = left ? "💡 Hint (" + left + " left)" : "💡 No more hints";
    ui.hintBtn.disabled = !left;
    if (state.timer) state.timer.hints[q.id] = state.hintsShown;
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
    var q = state.current;
    if (!check || !q) {
      ui.status.textContent = "Ran in " + ms + " ms." + (q ? "  Click “Check answer” to grade it." : "");
      if (result.columns.length) ui.output.appendChild(table(result.columns, result.values));
      return;
    }
    var verdict = JobprepGrader.grade(result, q.expected, q.ordered);
    ui.status.className = "pg-status " + (verdict.ok ? "pg-good" : "pg-bad");
    ui.status.textContent = (verdict.ok ? "✅ " : "❌ ") + verdict.reason;
    if (verdict.ok) {
      state.progress.solved[q.id] = true; save(); fillSelect(); ui.select.value = String(q.id);
      if (state.timer && !(q.id in state.timer.solvedAt)) {
        state.timer.solvedAt[q.id] = (Date.now() - state.timer.start) / 1000;
        ui.status.textContent += "  Solved at " + mmss(state.timer.solvedAt[q.id]) + ".";
      }
    }
    ui.output.appendChild(el("h4", {}, ["Your result"]));
    ui.output.appendChild(table(result.columns, result.values));
    if (verdict.ok && isMock(q) && q.followups && q.followups.length) {
      var box = el("div", { class: "pg-followups" }, [el("h4", {}, ["🎤 The interviewer follows up…"])]);
      q.followups.forEach(function (f) {
        box.appendChild(el("div", { class: "pg-quote", html: f.question }));
        if (f.answer) box.appendChild(el("details", {}, [el("summary", {}, ["Answer out loud first, then compare with a model answer"]), el("div", { html: f.answer })]));
      });
      ui.output.insertBefore(box, ui.output.firstChild);
    }
    if (!verdict.ok && !isMock(q)) {
      ui.output.appendChild(el("h4", {}, ["Expected (first rows)"]));
      ui.output.appendChild(table(q.expected.columns, q.expected.rows.slice(0, 8)));
    }
  }

  function showSolution() {
    var q = state.current;
    if (!q) return;
    var counts = state.timer && !(q.id in state.timer.solvedAt);     // peeking after solving is fine
    var msg = counts ? "You're in a timed mock: looking at the solution now counts as not solving it. Show anyway?"
                     : "Show the reference solution?" + (state.progress.solved[q.id] ? "" : " Try for a few more minutes first!");
    if (!confirm(msg)) return;
    if (counts) state.timer.peeked[q.id] = true;
    ui.output.innerHTML = "";
    ui.output.appendChild(el("h4", {}, ["Reference solution"]));
    ui.output.appendChild(el("pre", { class: "pg-solution" }, [el("code", {}, [q.solution])]));
    ui.output.appendChild(el("button", { class: "md-button", onclick: function () { ui.editor.value = q.solution; ui.editor.dispatchEvent(new Event("input")); } }, ["Copy into editor"]));
  }

  function resetEditor() {
    if (!confirm("Clear your query for this question?")) return;
    var id = state.current ? state.current.id : 0;
    delete state.progress.drafts[id]; save(); pick(id);
  }

  function next() {
    var q = state.current, list = isMock(q) ? roundQs(q.round || 1) : state.questions;
    var i = q ? list.indexOf(q) : -1;
    var nxt = list[i + 1];
    pick(nxt ? nxt.id : (isMock(q) ? q.id : 0));
  }

  // ------------------------------------------------------------------ timed mock
  function toggleMock() {
    if (state.timer) { endMock(false); return; }
    if (!state.mock.length) return;
    var r = Number(ui.roundSel.value) || 1, qs = roundQs(r), name = (rounds().find(function (x) { return x.round === r; }) || {}).name;
    if (!qs.length) return;
    if (!confirm("Start a 45-minute mock: " + name + "?\n\nWork through " + range(qs) + " in order. Hints and solutions are there, " +
                 "but they're noted in your summary. Aim for " + range(qs.slice(0, 4)) + " within 30–35 minutes, and think out loud!")) return;
    qs.forEach(function (q) { delete state.progress.drafts[q.id]; });
    save();
    state.timer = { round: r, name: name, qs: qs, start: Date.now(), solvedAt: {}, hints: {}, peeked: {}, handle: setInterval(tick, 1000) };
    ui.timerBtn.textContent = "■ End mock";
    ui.roundSel.disabled = true;
    app.classList.add("pg-mock-running");
    pick(qs[0].id); tick();
  }

  function tick() {
    if (!state.timer) return;
    var left = MOCK_MINUTES * 60 - (Date.now() - state.timer.start) / 1000;
    ui.clock.textContent = "⏱ " + mmss(left);
    ui.clock.className = "pg-clock" + (left < 300 ? " pg-clock-low" : "");
    if (left <= 0) endMock(true);
  }

  function endMock(timeUp) {
    var t = state.timer;
    clearInterval(t.handle);
    state.timer = null;
    ui.timerBtn.textContent = "⏱ Start timed mock (45 min)";
    ui.roundSel.disabled = false;
    ui.clock.textContent = "";
    app.classList.remove("pg-mock-running");
    var elapsed = Math.min(MOCK_MINUTES * 60, (Date.now() - t.start) / 1000);
    var rows = t.qs.map(function (q) {
      var solved = q.id in t.solvedAt && !t.peeked[q.id];
      return [label(q) + " · " + q.title, solved ? "✓ " + mmss(t.solvedAt[q.id]) : (t.peeked[q.id] ? "peeked at solution" : "—"),
              String(t.hints[q.id] || 0)];
    });
    var core = t.qs.slice(0, 4).map(function (q) { return q.id; });
    var coreDone = core.every(function (id) { return id in t.solvedAt && !t.peeked[id] && t.solvedAt[id] <= 35 * 60; });
    var totalHints = Object.keys(t.hints).reduce(function (s, k) { return s + t.hints[k]; }, 0);
    var n = t.qs.filter(function (q) { return q.id in t.solvedAt && !t.peeked[q.id]; }).length;
    var pass = coreDone && totalHints <= 2;
    state.progress.mockHistory.push({ date: new Date().toISOString().slice(0, 10), round: t.round, solved: n, total: t.qs.length,
                                      minutes: Math.round(elapsed / 60), hints: totalHints, pass: pass });
    save();

    ui.output.innerHTML = ""; ui.hints.innerHTML = "";
    ui.status.className = "pg-status " + (pass ? "pg-good" : "pg-bad");
    var bar = range(t.qs.slice(0, 4)) + " within 35 min with ≤ 2 hints";
    ui.status.textContent = (timeUp ? "⏰ Time's up! " : "Mock ended. ") + t.name + ": you solved " + n + " of " + t.qs.length +
      " in " + mmss(elapsed) + " using " + totalHints + " hint(s). " +
      (pass ? "Pass signal ✅ (" + bar + ")." : "Not yet a pass signal: the bar is " + bar + ".");
    ui.output.appendChild(el("h4", {}, ["Your scorecard"]));
    ui.output.appendChild(table(["Question", "Solved at", "Hints used"], rows));
    var hist = state.progress.mockHistory.slice(-5).reverse();
    if (hist.length > 1) {
      ui.output.appendChild(el("h4", {}, ["Recent attempts"]));
      ui.output.appendChild(table(["Date", "Round", "Solved", "Minutes", "Hints", "Pass"], hist.map(function (h) {
        return [h.date, String(h.round || 1), h.solved + " / " + (h.total || 7), String(h.minutes), String(h.hints), h.pass ? "✅" : "—"];
      })));
    }
    ui.output.appendChild(el("p", {}, ["Now score yourself on the five rubric dimensions (framing, correctness, communication, business sense, verification) in the mock-interviews README, and review the follow-up questions for anything you skipped."]));
  }

  // ------------------------------------------------------------------ boot
  build();
  ui.status.textContent = "Loading SQLite (WebAssembly) and the ShopKart database…";
  Promise.all([
    initSqlJs({ locateFile: function (f) { return VENDOR + "/" + f; } }),
    fetch(BASE + "/shopkart.db").then(function (r) { if (!r.ok) throw new Error("database " + r.status); return r.arrayBuffer(); }),
    fetch(BASE + "/questions.json").then(function (r) { if (!r.ok) throw new Error("questions " + r.status); return r.json(); }),
    fetch(BASE + "/mock.json").then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; })
  ]).then(function (res) {
    state.db = new res[0].Database(new Uint8Array(res[1]));
    state.questions = res[2];
    state.mock = res[3];
    ui.roundSel.innerHTML = "";
    rounds().forEach(function (r) { ui.roundSel.appendChild(el("option", { value: String(r.round) }, [r.name + " (" + roundQs(r.round).length + " Qs)"])); });
    fillSelect(); fillSchema();
    var m = /#(q|m)(\d+)/.exec(location.hash);
    pick(m ? (m[1] === "m" ? "m" + m[2] : m[2]) : (/#scratch/.test(location.hash) ? 0 : 1));
    if (!state.mock.length) { ui.timerBtn.style.display = "none"; ui.roundSel.style.display = "none"; }
  }).catch(function (err) {
    ui.status.className = "pg-status pg-bad";
    ui.status.textContent = "Could not load the playground: " + err.message +
      ". If you opened this file directly from disk, serve the site over HTTP instead (mkdocs serve).";
  });
})();
