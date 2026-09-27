---
title: SQL Playground
hide:
  - toc
---

# SQL Playground

Practise all 40 SQL questions **in your browser**. There's nothing to install: SQLite runs locally in the page via
WebAssembly, on the full ShopKart database. Answers are graded instantly, and your queries and progress are saved in
this browser.

**🎤 New: timed mock interview.** Click **⏱ Start timed mock** for the
[live SQL round](../mock-interviews/01-live-sql-round.md): 7 fresh questions against a 45-minute clock, hints on
request, the interviewer's follow-up questions after each solve, and a scorecard at the end.

<link rel="stylesheet" href="../assets/playground/playground.css">
<div id="pg-app" data-base="." data-vendor="../assets/vendor/sql.js">Loading the playground… (JavaScript required)</div>
<script src="../assets/vendor/sql.js/sql-wasm.js"></script>
<script src="../assets/playground/grader.js"></script>
<script src="../assets/playground/playground.js"></script>

!!! tip "Tips"
    **Ctrl/⌘ + Enter** runs your query · click a table name in the schema panel to insert it · question links are
    shareable (`…/playground/#q30`, `#m3` for mock questions) · the grading rules match `python practice/sql/check.py` (column names don't
    matter; column count, values and, where stated, row order do). See the
    [conventions](../practice/sql/EXERCISES.md) for revenue and valid-order definitions.
