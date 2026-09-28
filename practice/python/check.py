"""
Grade practice/python/exercises.py against the reference solutions.

    python practice/python/check.py            # all attempted exercises
    python practice/python/check.py 4 17       # specific exercises
    python practice/python/check.py 4 --show   # print expected vs yours
    python practice/python/check.py --solutions  # sanity-check the reference file itself
"""
from __future__ import annotations

import importlib
import inspect
import math
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from data_loader import load_clean, load_raw  # noqa: E402

# Windows consoles/pipes default to cp1252, which can't print ✓ ✗ ₹ — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

GREEN, RED, DIM, YELLOW, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[33m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = YELLOW = RESET = ""

# exercises whose row order does NOT matter (everything else is compared in order)
UNORDERED = {"p06"}


def to_rows(obj):
    """Convert any result into a comparable structure."""
    if isinstance(obj, pd.Series):
        obj = obj.to_frame()
    if isinstance(obj, pd.DataFrame):
        df = obj
        if not isinstance(df.index, pd.RangeIndex) or df.index.name is not None:
            df = df.reset_index()
        return [tuple(norm(v) for v in row) for row in df.itertuples(index=False, name=None)]
    if isinstance(obj, dict):
        return {k: norm(v) for k, v in obj.items()}
    return norm(obj)


def norm(v):
    if isinstance(v, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(v).date()) if pd.Timestamp(v) == pd.Timestamp(v).normalize() else str(pd.Timestamp(v))
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        if math.isnan(v):
            return "NaN"
        return round(float(v), 2) + 0.0
    if v is None or v is pd.NaT or (not isinstance(v, str) and pd.isna(v)):
        return "NaN"
    return v


def same(a, b):
    if isinstance(a, float) and isinstance(b, (int, float)) or isinstance(b, float) and isinstance(a, (int, float)):
        return abs(a - b) <= 0.011
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    return a == b


def show(label, obj):
    print(f"    {YELLOW}{label}:{RESET}")
    text = obj.head(8).to_string() if isinstance(obj, (pd.DataFrame, pd.Series)) else repr(obj)
    for line in text.splitlines():
        print("      " + line)


def main(argv):
    show_all = "--show" in argv
    target = "solutions" if "--solutions" in argv else "exercises"
    ids = {int(a) for a in argv if a.isdigit()}
    mine = importlib.import_module(target)
    ref = importlib.import_module("solutions")

    data = {**load_clean(), **load_raw()}
    data["city"] = data["customers_raw"]["city"]           # Series inputs for p02 / p03
    data["dates"] = data["customers_raw"]["signup_date"]
    funcs = sorted(name for name, f in inspect.getmembers(ref, inspect.isfunction)
                   if name[:1] == "p" and name[1:3].isdigit())
    res = {"pass": 0, "fail": 0, "todo": 0}
    for name in funcs:
        num = int(name[1:3])
        if ids and num not in ids:
            continue
        fn = getattr(mine, name, None)
        kwargs_for = lambda f: {p: data[p].copy() for p in inspect.signature(f).parameters if p in data}  # noqa: E731
        try:
            got = fn(**kwargs_for(fn))
        except NotImplementedError:
            res["todo"] += 1
            continue
        except Exception as e:  # noqa: BLE001
            print(f"{RED}✗ {name}: raised {type(e).__name__}: {e}{RESET}")
            print(DIM + "".join(traceback.format_exc().splitlines(True)[-3:]) + RESET)
            res["fail"] += 1
            continue
        expected = getattr(ref, name)(**kwargs_for(getattr(ref, name)))
        a, b = to_rows(got), to_rows(expected)
        if name[:3] in UNORDERED and isinstance(a, list) and isinstance(b, list):
            a, b = sorted(a, key=str), sorted(b, key=str)
        ok = same(a, b)
        print(f"{GREEN}✓ {name}{RESET}" if ok else f"{RED}✗ {name}: result differs from reference{RESET}")
        if show_all or not ok:
            show("expected", expected)
            show("yours", got)
        res["pass" if ok else "fail"] += 1
    print(f"\n{GREEN}{res['pass']} passed{RESET} · {RED}{res['fail']} failed{RESET} · "
          f"{DIM}{res['todo']} not attempted{RESET}")
    return 0 if res["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
