---
title: SQL Playground
hide:
  - toc
---

# SQL Playground

Practise all 60 SQL questions **in your browser**. There's nothing to install: SQLite runs locally in the page via
WebAssembly, on the full ShopKart database. Answers are graded instantly, and your queries and progress are saved in
this browser.

**🎤 Timed mock interviews.** Pick a round next to the timer and click **⏱ Start timed mock**:
[round 1 · core SQL](../mock-interviews/01-live-sql-round.md) (7 questions),
[round 2 · product & marketing](../mock-interviews/05-live-sql-round-2.md) (6) or
[round 3 · advanced](../mock-interviews/06-live-sql-round-3.md) (6). You get fresh questions (none are in the practice set)
against a 45-minute clock, hints on request, the interviewer's follow-up questions after each solve, and a scorecard at
the end.

<link rel="stylesheet" href="../assets/playground/playground.css">
<div id="pg-app" data-base="." data-vendor="../assets/vendor/sql.js">Loading the playground… (JavaScript required)</div>
<script src="../assets/vendor/sql.js/sql-wasm.js"></script>
<script src="../assets/playground/grader.js"></script>
<script src="../assets/playground/playground.js"></script>

!!! tip "Tips"
    **Ctrl/⌘ + Enter** runs your query · click a table name in the schema panel to insert it · question links are
    shareable (`…/playground/#q30`, `#m3` for mock questions, numbered across rounds: round 2 starts at `#m8`, round 3 at `#m14`) · the grading rules match `python practice/sql/check.py` (column names don't
    matter; column count, values and, where stated, row order do). See the
    [conventions](../practice/sql/EXERCISES.md) for revenue and valid-order definitions.
