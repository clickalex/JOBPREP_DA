"""Helpers to load the ShopKart datasets as pandas DataFrames.

    from data_loader import load_clean, load_raw
    d = load_clean()          # dict of DataFrames with dates parsed
    orders = d["orders"]
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"


def load_clean() -> dict[str, pd.DataFrame]:
    """Analysis-ready tables. Timestamps are parsed to datetime64."""
    c = DATA / "clean"
    return {
        "customers": pd.read_csv(c / "customers.csv", parse_dates=["signup_date"]),
        "products": pd.read_csv(c / "products.csv", parse_dates=["launch_date"]),
        "orders": pd.read_csv(c / "orders.csv", parse_dates=["order_ts"]),
        "items": pd.read_csv(c / "order_items.csv"),
        "sessions": pd.read_csv(c / "web_sessions.csv", parse_dates=["session_start"]),
        "experiment": pd.read_csv(c / "checkout_experiment.csv", parse_dates=["assigned_at"]),
        "employees": pd.read_csv(c / "employees.csv", parse_dates=["hire_date"]),
    }


def load_raw() -> dict[str, pd.DataFrame]:
    """Messy exports exactly as a source system might hand them over (read with defaults)."""
    r = DATA / "raw"
    return {
        "customers_raw": pd.read_csv(r / "customers_raw.csv"),
        "orders_raw": pd.read_csv(r / "orders_raw.csv"),
        "items_raw": pd.read_csv(r / "order_items_raw.csv"),
        "products": pd.read_csv(r / "products.csv"),
    }


VALID_STATUSES = ["Delivered", "Shipped"]


def with_line_revenue(items: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of order_items with a `net_revenue` column."""
    out = items.copy()
    out["net_revenue"] = out["quantity"] * out["unit_price"] - out["discount"]
    return out
