"""The dataset is the foundation of every exercise: it must be intact and exactly reproducible."""
import hashlib
import shutil
import sqlite3
import subprocess
import sys

import pandas as pd
import pytest

from conftest import ROOT

DATA = ROOT / "data"
TABLES = ["customers", "products", "orders", "order_items", "web_sessions", "checkout_experiment", "employees"]
ROW_COUNTS = {"customers": 8000, "products": 48, "orders": 11885, "order_items": 20298,
              "web_sessions": 40000, "checkout_experiment": 24000, "employees": 30}


def manifest():
    lines = (DATA / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    return {path: digest for digest, path in (ln.split(maxsplit=1) for ln in lines if ln.strip())}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_csv_files_match_checksums():
    m = manifest()
    assert len(m) == 11
    bad = [p for p, digest in m.items() if sha256(DATA / p) != digest]
    assert not bad, f"data files changed (or checked out with CRLF line endings): {bad}"


def test_database_row_counts():
    con = sqlite3.connect(DATA / "shopkart.db")
    got = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
    assert got == ROW_COUNTS


def test_database_matches_clean_csvs():
    con = sqlite3.connect(DATA / "shopkart.db")
    for t in ["products", "orders", "employees"]:
        db = pd.read_sql(f"SELECT * FROM {t}", con)
        csv = pd.read_csv(DATA / "clean" / f"{t}.csv")
        assert list(db.columns) == list(csv.columns), t
        pd.testing.assert_frame_equal(db, csv, check_dtype=False, check_exact=False, rtol=1e-9)


def test_foreign_keys_hold():
    con = sqlite3.connect(DATA / "shopkart.db")
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []


def test_generator_is_deterministic(tmp_path):
    """Re-run the generator in a scratch folder; every CSV must be byte-identical and the DB content equal."""
    shutil.copy(DATA / "generate_data.py", tmp_path)
    shutil.copy(DATA / "schema.sql", tmp_path)
    subprocess.run([sys.executable, str(tmp_path / "generate_data.py")], check=True, capture_output=True, cwd=tmp_path)
    m = manifest()
    bad = [p for p, digest in m.items() if sha256(tmp_path / p) != digest]
    assert not bad, f"regenerated files differ: {bad}"
    a, b = sqlite3.connect(DATA / "shopkart.db"), sqlite3.connect(tmp_path / "shopkart.db")
    for t in TABLES:   # compare content, not bytes (page layout can differ between SQLite versions)
        q = f"SELECT * FROM {t} ORDER BY 1"
        assert a.execute(q).fetchall() == b.execute(q).fetchall(), t


@pytest.mark.parametrize("f", ["customers_raw.csv", "orders_raw.csv", "order_items_raw.csv"])
def test_raw_data_is_still_messy(f):
    """The raw files exist to be cleaned: make sure nobody 'fixed' them by accident."""
    df = pd.read_csv(DATA / "raw" / f, dtype=str)
    assert df.duplicated().sum() > 0 or df.isna().sum().sum() > 0
