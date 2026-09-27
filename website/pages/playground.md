---
title: SQL Playground
hide:
  - toc
---

# SQL Playground

Practise all 40 SQL questions **in your browser**. There's nothing to install: SQLite runs locally in the page via
WebAssembly, on the full ShopKart database. Answers are graded instantly, and your queries and progress are saved in
this browser.

<link rel="stylesheet" href="../assets/playground/playground.css">
<div id="pg-app" data-base="." data-vendor="../assets/vendor/sql.js">Loading the playground… (JavaScript required)</div>
<script src="../assets/vendor/sql.js/sql-wasm.js"></script>
<script src="../assets/playground/grader.js"></script>
<script src="../assets/playground/playground.js"></script>

!!! tip "Tips"
    **Ctrl/⌘ + Enter** runs your query · click a table name in the schema panel to insert it · question links are
    shareable (`…/playground/#q30`) · the grading rules match `python practice/sql/check.py` (column names don't
    matter; column count, values and, where stated, row order do). See the
    [conventions](../practice/sql/EXERCISES.md) for revenue and valid-order definitions.
