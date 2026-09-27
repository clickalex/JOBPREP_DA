/*
 * JOBPREP_DA SQL grader: shared by the browser playground and the Node test suite.
 * Mirrors practice/sql/check.py:
 *   - column COUNT must match (names don't matter)
 *   - row count must match
 *   - numbers compared with a 0.006 tolerance (≈ "equal to 2 decimals")
 *   - row order only matters when the question says so
 */
(function (root) {
  "use strict";

  var TOL = 0.006;

  function normCell(v) {
    if (v === undefined) return null;
    if (typeof v === "number" && Object.is(v, -0)) return 0;
    if (v instanceof Uint8Array) return "[blob]";
    return v;
  }

  function sortKey(row) {
    return JSON.stringify(row.map(function (v) {
      return typeof v === "number" ? Number(v.toFixed(2)) : v;
    }));
  }

  function cellEq(a, b) {
    if (typeof a === "number" && typeof b === "number") return Math.abs(a - b) <= TOL;
    return a === b;
  }

  function rowsEq(a, b) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i].length !== b[i].length) return false;
      for (var j = 0; j < a[i].length; j++) if (!cellEq(a[i][j], b[i][j])) return false;
    }
    return true;
  }

  function sorted(rows) {
    return rows.slice().sort(function (x, y) {
      var kx = sortKey(x), ky = sortKey(y);
      return kx < ky ? -1 : kx > ky ? 1 : 0;
    });
  }

  /**
   * grade(result, expected, ordered)
   *   result   = {columns: [...], values: [[...], ...]}   (sql.js exec() shape)
   *   expected = {columns: [...], rows:   [[...], ...]}
   * returns {ok: bool, reason: string}
   */
  function grade(result, expected, ordered) {
    var got = (result && result.values ? result.values : []).map(function (r) { return r.map(normCell); });
    var gotCols = result && result.columns ? result.columns : [];
    var exp = expected.rows.map(function (r) { return r.map(normCell); });

    if (gotCols.length !== expected.columns.length) {
      return { ok: false, reason: "Expected " + expected.columns.length + " column(s) (" +
        expected.columns.join(", ") + "), got " + gotCols.length + "." };
    }
    if (got.length !== exp.length) {
      return { ok: false, reason: "Expected " + exp.length + " row(s), got " + got.length + "." };
    }
    if (ordered) {
      if (rowsEq(got, exp)) return { ok: true, reason: "Correct!" };
      if (rowsEq(sorted(got), sorted(exp))) return { ok: false, reason: "Right rows, wrong ORDER — check your ORDER BY." };
      return { ok: false, reason: "Values differ from the expected result." };
    }
    if (rowsEq(sorted(got), sorted(exp))) return { ok: true, reason: "Correct!" };
    return { ok: false, reason: "Values differ from the expected result." };
  }

  /**
   * Run possibly-multiple statements and return the LAST result set (or an empty one).
   * Uses iterateStatements rather than db.exec(): exec() drops result sets with zero rows, so a
   * correct query whose answer is "no rows" would lose its column names and be graded as wrong.
   */
  function runSql(db, sql) {
    var last = { columns: [], values: [] };
    if (typeof db.iterateStatements !== "function") {   // very old sql.js
      var res = db.exec(sql);
      return res.length ? res[res.length - 1] : last;
    }
    var it = db.iterateStatements(sql), step, stmt;
    while (!(step = it.next()).done) {
      stmt = step.value;
      try {
        var cols = stmt.getColumnNames(), values = [];
        while (stmt.step()) values.push(stmt.get());
        if (cols.length) last = { columns: cols, values: values };
      } finally {
        stmt.free();
      }
    }
    return last;
  }

  var api = { grade: grade, runSql: runSql, TOLERANCE: TOL };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.JobprepGrader = api;
})(this);
