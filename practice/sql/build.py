"""
Regenerate EXERCISES.md, SOLUTIONS.md and starter files from questions.py.

    python practice/sql/build.py

Starter files in my_answers/ are only created if they don't exist, so your
work is never overwritten.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from questions import QUESTIONS  # noqa: E402

# Windows consoles/pipes default to cp1252, which can't print ✓ ✗ ₹ — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HEADER = """\
> **Conventions (apply to every question)**
> * **Net line revenue** = `quantity * unit_price - discount` (INR, from `order_items`)
> * A **valid order** has `status IN ('Delivered', 'Shipped')` — cancelled & returned orders earn nothing
> * Revenue **excludes shipping fees** unless stated
> * Round money to **2 dp** and percentages to **1 dp** (unless stated)
> * Dialect is **SQLite** — dates are ISO text, so use `strftime('%Y-%m', col)` and `julianday()`.
>   The [SQL guide](../../study-guide/01-sql.md#7-dialect-cheat-sheet) maps these to PostgreSQL / MySQL / SQL Server.
"""


def md_table(cols, rows, limit=6):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows[:limit]:
        out.append("| " + " | ".join("NULL" if v is None else (f"{v:,.2f}" if isinstance(v, float) else str(v)) for v in r) + " |")
    if len(rows) > limit:
        out.append(f"| … {len(rows) - limit} more rows |" + " |" * (len(cols) - 1))
    return "\n".join(out)


def main():
    con = sqlite3.connect(ROOT / "data" / "shopkart.db")
    ex = ["# SQL Practice — 40 interview-style questions\n",
          "Database: `data/shopkart.db` (see the [data dictionary](../../data/README.md)). "
          "Write each answer in `my_answers/qNN.sql`, then grade yourself with "
          "`python practice/sql/check.py`.\n", HEADER,
          "\n| # | Level | Topic | Title |\n|---|---|---|---|"]
    for q in QUESTIONS:
        ex.append(f"| [{q['id']}](#q{q['id']:02d}) | {q['level']} | {q['topics']} | {q['title']} |")
    sol = ["# SQL Practice — Reference solutions\n",
           "Try each question first! Many have more than one correct approach — `check.py` compares "
           "*results*, not query text.\n"]

    current = None
    for q in QUESTIONS:
        if q["level"] != current:
            current = q["level"]
            ex.append(f"\n## {current}\n")
            sol.append(f"\n## {current}\n")
        cur = con.execute(q["solution"])
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        order_note = "row order matters" if q["ordered"] else "any row order"
        ex.append(f"### Q{q['id']:02d}\n**{q['title']}** · _{q['topics']}_\n\n{q['prompt']}\n\n"
                  f"Expected columns: `{', '.join(cols)}` · {len(rows)} row(s) · {order_note}\n")
        sol.append(f"### Q{q['id']:02d} — {q['title']}\n\n```sql\n{q['solution'].strip()}\n```\n\n"
                   f"<details><summary>Expected output</summary>\n\n{md_table(cols, rows)}\n\n</details>\n")

        starter = HERE / "my_answers" / f"q{q['id']:02d}.sql"
        starter.parent.mkdir(exist_ok=True)
        if not starter.exists():
            prompt = q["prompt"].replace("**", "").replace("*", "").replace("`", "")
            wrapped = "\n".join("-- " + line for line in prompt.splitlines())
            starter.write_text(f"-- Q{q['id']:02d}: {q['title']}  [{q['level']}]\n{wrapped}\n"
                               f"-- Expected columns: {', '.join(cols)}\n\n", encoding="utf-8")

    (HERE / "EXERCISES.md").write_text("\n".join(ex) + "\n", encoding="utf-8")
    (HERE / "SOLUTIONS.md").write_text("\n".join(sol) + "\n", encoding="utf-8")
    print(f"Wrote EXERCISES.md, SOLUTIONS.md and starters for {len(QUESTIONS)} questions.")


if __name__ == "__main__":
    main()
