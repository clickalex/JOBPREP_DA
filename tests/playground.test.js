// Headless test of the browser SQL playground: the same grader.js + vendored sql.js + generated questions.json.
// Run: python website/build_site.py && node tests/playground.test.js
"use strict";
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const ROOT = path.resolve(__dirname, "..");
const VENDOR = path.join(ROOT, "website/assets/vendor/sql.js");
const STAGE = path.join(ROOT, "website/_build_docs/playground");
const initSqlJs = require(path.join(VENDOR, "sql-wasm.js"));
const { grade, runSql } = require(path.join(ROOT, "website/assets/playground/grader.js"));

(async () => {
  const SQL = await initSqlJs({ locateFile: (f) => path.join(VENDOR, f) });
  const db = new SQL.Database(fs.readFileSync(path.join(STAGE, "shopkart.db")));
  const questions = JSON.parse(fs.readFileSync(path.join(STAGE, "questions.json"), "utf8"));
  assert.strictEqual(questions.length, 40, "expected 40 questions");

  let failures = 0;
  const fail = (msg) => { failures++; console.error("FAIL " + msg); };

  // 1. every reference solution, executed by sql.js in "browser" conditions, passes the grader
  for (const q of questions) {
    let v;
    try { v = grade(runSql(db, q.solution), q.expected, q.ordered); }
    catch (e) { fail(`Q${q.id} solution threw: ${e.message}`); continue; }
    if (!v.ok) fail(`Q${q.id} reference solution rejected: ${v.reason}`);
  }

  // 2. wrong answers are rejected, each for the right reason
  const q = (id) => questions.find((x) => x.id === id);
  const expectFail = (label, result, question, pattern) => {
    const v = grade(result, question.expected, question.ordered);
    if (v.ok) fail(`${label}: wrong answer was accepted`);
    else if (pattern && !pattern.test(v.reason)) fail(`${label}: unexpected reason "${v.reason}"`);
  };
  const q3 = q(3);
  const good3 = runSql(db, q3.solution);
  expectFail("extra column", { columns: [...good3.columns, "x"], values: good3.values.map((r) => [...r, 1]) }, q3, /column/);
  expectFail("missing row", { columns: good3.columns, values: good3.values.slice(1) }, q3, /row/);
  expectFail("changed value", { columns: good3.columns, values: good3.values.map((r, i) => (i ? r : r.map((c) => (typeof c === "number" ? c + 1 : c)))) }, q3, /Values/);
  expectFail("empty result", runSql(db, "SELECT 1 WHERE 0"), q3, /column|row/);

  const ordered = questions.find((x) => x.ordered && x.expected.rows.length > 2);
  const good = runSql(db, ordered.solution);
  expectFail(`Q${ordered.id} reversed order`, { columns: good.columns, values: [...good.values].reverse() }, ordered, /ORDER/);

  const unordered = questions.find((x) => !x.ordered && x.expected.rows.length >= 2);
  const gu = runSql(db, unordered.solution);
  const vu = grade({ columns: gu.columns, values: [...gu.values].reverse() }, unordered.expected, false);
  if (!vu.ok) fail(`Q${unordered.id}: row order should not matter but got "${vu.reason}"`);

  // 3. tolerance: tiny float noise passes, a 0.01 difference fails
  const q9 = q(9);
  const r9 = runSql(db, q9.solution);
  const nudge = (d) => ({ columns: r9.columns, values: r9.values.map((r) => r.map((c) => (typeof c === "number" ? c + d : c))) });
  if (!grade(nudge(0.004), q9.expected, q9.ordered).ok) fail("0.004 float noise should pass");
  if (grade(nudge(0.02), q9.expected, q9.ordered).ok) fail("0.02 difference should fail");

  // 4. SQL errors surface as exceptions (the UI shows them)
  assert.throws(() => runSql(db, "SELEC nonsense"), /syntax error/);

  if (failures) { console.error(`\n${failures} playground check(s) failed`); process.exit(1); }
  console.log(`playground OK: 40/40 reference solutions pass in sql.js; wrong answers rejected (sql.js SQLite ${db.exec("select sqlite_version()")[0].values[0][0]})`);
})().catch((e) => { console.error(e); process.exit(1); });
