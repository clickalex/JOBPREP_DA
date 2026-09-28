"""
One-screen progress report across the SQL and pandas practice sets.

    python progress.py

Runs both auto-graders quietly and shows how far you've got, what's failing and what to try next.
(The Excel workbook grades itself in its Result column, and browser-playground progress lives in your browser.)
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
STRIP = re.compile(r"\033\[[0-9;]*m")


def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_quiet(mod, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.main(argv)
    return STRIP.sub("", buf.getvalue())


def bar(done, total, width=30):
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def summarise(label, out, total, nxt_hint):
    passed = int(re.search(r"(\d+) passed", out).group(1))
    failed_lines = [ln.strip("✗ ").strip() for ln in out.splitlines() if ln.startswith("✗")]
    print(f"\n{label}")
    print(f"  {bar(passed, total)}  {passed}/{total} passed ({100 * passed // total}%)")
    if failed_lines:
        print(f"  Failing ({len(failed_lines)}):")
        for ln in failed_lines[:5]:
            print(f"    ✗ {ln[:90]}")
        if len(failed_lines) > 5:
            print(f"    … and {len(failed_lines) - 5} more")
    print(f"  Next: {nxt_hint}")
    return passed


def main():
    sql = load("sql_check", ROOT / "practice" / "sql" / "check.py")
    sql_out = run_quiet(sql, [])
    solved = {int(m) for m in re.findall(r"✓ Q(\d+)", sql_out)}
    todo = [q for q in sql.QUESTIONS if q["id"] not in solved]
    nxt = f"Q{todo[0]['id']:02d} {todo[0]['title']} ({todo[0]['level']}) → practice/sql/my_answers/q{todo[0]['id']:02d}.sql" if todo else "all done 🎉 → try a mock interview (mock-interviews/)"
    s = summarise(f"SQL · {len(sql.QUESTIONS)} questions", sql_out, len(sql.QUESTIONS), nxt)

    py = load("py_check", ROOT / "practice" / "python" / "check.py")
    py_out = run_quiet(py, [])
    import exercises  # noqa: E402  (importable after load() added the folder to sys.path)
    names = sorted(n for n in dir(exercises) if n[:1] == "p" and n[1:3].isdigit())
    done_py = {m for m in re.findall(r"✓ (p\d\d\w*)", py_out)}
    todo_py = [n for n in names if n not in done_py]
    nxt_py = f"{todo_py[0]} in practice/python/exercises.py" if todo_py else "all done 🎉 → build your own portfolio project"
    p = summarise(f"pandas · {len(names)} exercises", py_out, len(names), nxt_py)

    total = s + p
    grand = len(sql.QUESTIONS) + len(names)
    print(f"\nOverall: {bar(total, grand)}  {total}/{grand}")
    print("Excel: open practice/excel/ShopKart_Excel_Practice.xlsx; the Result column grades each task.\n")


if __name__ == "__main__":
    main()
