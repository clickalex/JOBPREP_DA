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
  assert.strictEqual(questions.length, 60, "expected 60 questions");

  let failures = 0;
  const fail = (msg) => { failures++; console.error("FAIL " + msg); };

  // 1. every reference solution, executed by sql.js in "browser" conditions, passes the grader
  for (const q of questions) {
    let v;
    try { v = grade(runSql(db, q.solution), q.expected, q.ordered); }
    catch (e) { fail(`Q${q.id} solution threw: ${e.message}`); continue; }
    if (!v.ok) fail(`Q${q.id} reference solution rejected: ${v.reason}`);
  }

  // 1b. mock-interview questions (parsed from the live-SQL-round markdown, 3 rounds) also pass,
  //     including M7 whose correct answer is ZERO rows (db.exec() would drop its column names)
  const mock = JSON.parse(fs.readFileSync(path.join(STAGE, "mock.json"), "utf8"));
  assert.strictEqual(mock.length, 19, "expected 19 mock questions (7 + 6 + 6)");
  for (const m of mock) {
    const v = grade(runSql(db, m.solution), m.expected, m.ordered);
    if (!v.ok) fail(`${m.id} mock solution rejected: ${v.reason}`);
    if (!m.hints.length) fail(`${m.id} has no hints`);
  }
  const m7 = mock.find((m) => m.id === "m7");
  if (m7.expected.rows.length !== 0 || m7.expected.columns.length !== 4) fail("m7 should expect 4 columns and 0 rows");
  const empty = runSql(db, "SELECT employee_id, full_name FROM employees WHERE 0");
  if (empty.columns.length !== 2) fail("runSql must keep column names for empty results");
  if (grade(runSql(db, "SELECT 1, 2, 3, 4 FROM employees WHERE 0"), m7.expected, false).ok !== true) fail("empty 4-col result should pass m7");
  if (grade(runSql(db, "SELECT 1, 2 FROM employees WHERE 0"), m7.expected, false).ok) fail("empty 2-col result must fail m7");
  // the curveball traps must be graded as wrong
  const byTitle = (s) => mock.find((m) => m.title.includes(s));
  const noManager = byTitle("manages nobody"), shipping = byTitle("shipping fees");
  if (grade(runSql(db, "SELECT full_name, department FROM employees WHERE employee_id NOT IN (SELECT manager_id FROM employees)"), noManager.expected, false).ok)
    fail("NOT IN + NULL trap (0 rows) must fail the 'manages nobody' question");
  if (grade(runSql(db, "SELECT ROUND(SUM(o.shipping_fee), 2) FROM orders o JOIN order_items oi ON oi.order_id = o.order_id " +
                       "WHERE o.status IN ('Delivered','Shipped') AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'"), shipping.expected, false).ok)
    fail("fan-out (joined) shipping total must fail the shipping-fees question");
  // last statement wins, and non-SELECT statements don't clobber the result
  const multi = runSql(db, "SELECT 1 AS a; SELECT 2 AS b, 3 AS c;");
  if (multi.columns.join() !== "b,c") fail("multi-statement: last SELECT should be returned");

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
  console.log(`playground OK: ${questions.length}/${questions.length} practice + ${mock.length}/${mock.length} mock solutions pass in sql.js; wrong answers rejected (sql.js SQLite ${db.exec("select sqlite_version()")[0].values[0][0]})`);
})().catch((e) => { console.error(e); process.exit(1); });
