"""
Grade your SQL answers against the reference solutions.

Write each answer in practice/sql/my_answers/qNN.sql, then run from the repo root:

    python practice/sql/check.py            # check every answer you've written
    python practice/sql/check.py 7 12 30    # check specific questions
    python practice/sql/check.py 7 --show   # also print expected vs. your output

How grading works
  * Your query runs against data/shopkart.db (read-only).
  * Results are compared value-by-value (floats to 2 decimals). Column NAMES
    don't matter, column COUNT and ORDER do.
  * Row order only matters when the question asks for a specific order.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DB = ROOT / "data" / "shopkart.db"
ANSWERS = HERE / "my_answers"
sys.path.insert(0, str(HERE))
from questions import QUESTIONS  # noqa: E402

# Windows consoles/pipes default to cp1252, which can't print ✓ ✗ ₹ — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = DIM = RESET = ""


def connect() -> sqlite3.Connection:
    if not DB.exists():
        sys.exit(f"Database not found at {DB}. Run: python data/generate_data.py")
    return sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True)


def normalise(rows, ordered: bool):
    def norm(v):
        if isinstance(v, float):
            v = round(v, 2)
            return 0.0 if v == 0 else v  # -0.0 -> 0.0
        return v
    out = [tuple(norm(v) for v in r) for r in rows]
    return out if ordered else sorted(out, key=lambda r: tuple((x is None, str(x)) for x in r))


def run(con, sql: str):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, cur.fetchall()


def strip_comments(sql: str) -> str:
    lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("--")]
    return "\n".join(lines).strip()


def preview(cols, rows, limit=8):
    print(f"      {DIM}{' | '.join(cols)}{RESET}")
    for r in rows[:limit]:
        print("      " + " | ".join("NULL" if v is None else str(v) for v in r))
    if len(rows) > limit:
        print(f"      {DIM}... {len(rows) - limit} more rows{RESET}")


def check(con, q: dict, show: bool) -> str:
    path = ANSWERS / f"q{q['id']:02d}.sql"
    user_sql = strip_comments(path.read_text(encoding="utf-8-sig")) if path.exists() else ""
    if not user_sql:
        return "todo"
    exp_cols, exp_rows = run(con, q["solution"])
    try:
        got_cols, got_rows = run(con, user_sql)
    except sqlite3.Error as e:
        print(f"{RED}✗ Q{q['id']:02d} {q['title']}: SQL error → {e}{RESET}")
        return "fail"

    ok, why = True, ""
    if len(got_cols) != len(exp_cols):
        ok, why = False, f"expected {len(exp_cols)} columns {exp_cols}, got {len(got_cols)} {got_cols}"
    elif len(got_rows) != len(exp_rows):
        ok, why = False, f"expected {len(exp_rows)} rows, got {len(got_rows)}"
    elif normalise(got_rows, q["ordered"]) != normalise(exp_rows, q["ordered"]):
        if not q["ordered"] or normalise(got_rows, False) != normalise(exp_rows, False):
            why = "values differ"
        else:
            why = "right rows, wrong ORDER"
        ok = False

    if ok:
        print(f"{GREEN}✓ Q{q['id']:02d} {q['title']}{RESET}")
    else:
        print(f"{RED}✗ Q{q['id']:02d} {q['title']}: {why}{RESET}")
    if show or not ok:
        print(f"    {YELLOW}expected:{RESET}")
        preview(exp_cols, exp_rows)
        print(f"    {YELLOW}yours:{RESET}")
        preview(got_cols, got_rows)
    return "pass" if ok else "fail"


def main(argv):
    show = "--show" in argv
    ids = {int(a) for a in argv if a.isdigit()}
    qs = [q for q in QUESTIONS if not ids or q["id"] in ids]
    con = connect()
    results = {"pass": 0, "fail": 0, "todo": 0}
    for q in qs:
        results[check(con, q, show)] += 1
    total = len(qs)
    print(f"\n{GREEN}{results['pass']} passed{RESET} · {RED}{results['fail']} failed{RESET} · "
          f"{DIM}{results['todo']} not attempted{RESET} · {total} total")
    return 0 if results["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
