"""
Cleaning pipeline for the raw ShopKart exports.

Every fix is logged so the notebook can show a data-quality report
(what was wrong, how many rows, what we did) — the part interviewers
always ask about.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[3] / "data" / "raw"

CITY_ALIASES = {"Bangalore": "Bengaluru", "New Delhi": "Delhi", "Bombay": "Mumbai",
                "Gurgaon": "Gurugram", "Calcutta": "Kolkata", "Madras": "Chennai"}
REGION = {"Delhi": "North", "Gurugram": "North", "Noida": "North", "Lucknow": "North", "Jaipur": "North",
          "Chandigarh": "North", "Mumbai": "West", "Pune": "West", "Ahmedabad": "West", "Indore": "West",
          "Bengaluru": "South", "Hyderabad": "South", "Chennai": "South", "Kochi": "South", "Kolkata": "East"}
PAYMENT_MAP = {"cod": "Cash on Delivery", "cash on delivery": "Cash on Delivery", "upi": "UPI",
               "credit card": "Credit Card", "cc": "Credit Card", "debit card": "Debit Card",
               "dc": "Debit Card", "net banking": "Net Banking"}


@dataclass
class QualityLog:
    rows: list = field(default_factory=list)

    def add(self, table: str, issue: str, n: int, action: str):
        self.rows.append({"table": table, "issue": issue, "rows_affected": int(n), "action": action})

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)


def load_raw() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.read_csv(RAW / "customers_raw.csv"),
        "orders": pd.read_csv(RAW / "orders_raw.csv"),
        "items": pd.read_csv(RAW / "order_items_raw.csv"),
        "products": pd.read_csv(RAW / "products.csv"),
    }


def parse_mixed_dates(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"]:
        out = out.fillna(pd.to_datetime(s, format=fmt, errors="coerce"))
    return out


def clean_customers(df: pd.DataFrame, log: QualityLog) -> pd.DataFrame:
    df = df.copy()
    n = df.duplicated().sum()
    df = df.drop_duplicates()
    log.add("customers", "Exact duplicate rows", n, "Dropped")

    for col in ["first_name", "last_name"]:
        df[col] = df[col].str.strip()
    n = df.duplicated(subset="customer_id").sum()
    df = df.drop_duplicates(subset="customer_id", keep="first")
    log.add("customers", "Near-duplicates (same customer_id, stray whitespace)", n, "Trimmed, kept first")

    raw_city = df["city"].copy()
    df["city"] = df["city"].str.strip().str.title().replace(CITY_ALIASES)
    log.add("customers", "City spelling / casing variants (Bangalore, NEW DELHI…)", (raw_city != df["city"]).sum(),
            "Standardised to official names")
    df["region"] = df["city"].map(REGION)

    parsed = parse_mixed_dates(df["signup_date"])
    n_nonstd = (~df["signup_date"].str.match(r"^\d{4}-\d{2}-\d{2}$")).sum()
    log.add("customers", "signup_date in mixed formats (dd/mm/yyyy, dd Mon yyyy)", n_nonstd, "Parsed all 3 formats")
    df["signup_date"] = parsed

    n_upper = (df["email"].notna() & (df["email"] != df["email"].str.lower())).sum()
    df["email"] = df["email"].str.strip().str.lower()
    log.add("customers", "Upper-case emails", n_upper, "Lower-cased")
    log.add("customers", "Missing email", df["email"].isna().sum(), "Kept (not needed for analysis)")

    n = df["acquisition_channel"].isna().sum()
    df["acquisition_channel"] = df["acquisition_channel"].fillna("Unknown")
    log.add("customers", "Missing acquisition_channel", n, "Labelled 'Unknown'")
    return df.sort_values("customer_id").reset_index(drop=True)


def clean_orders(df: pd.DataFrame, log: QualityLog) -> pd.DataFrame:
    df = df.copy()
    n = df.duplicated().sum()
    df = df.drop_duplicates()
    log.add("orders", "Exact duplicate rows", n, "Dropped")

    raw = df["status"].copy()
    df["status"] = df["status"].str.strip().str.title()
    log.add("orders", "Status casing / trailing spaces ('delivered ', 'CANCELLED')", (raw != df["status"]).sum(),
            "Trimmed + Title Case")

    raw = df["payment_method"].copy()
    key = df["payment_method"].str.strip().str.lower()
    df["payment_method"] = key.map(PAYMENT_MAP).fillna(df["payment_method"])
    log.add("orders", "Payment method variants (COD, upi, CC…)", (raw != df["payment_method"]).sum(),
            "Mapped to 5 canonical values")
    df["order_ts"] = pd.to_datetime(df["order_ts"])
    return df.sort_values("order_id").reset_index(drop=True)


def clean_items(df: pd.DataFrame, products: pd.DataFrame, log: QualityLog) -> pd.DataFrame:
    df = df.copy()
    n = (df["quantity"] < 0).sum()
    df["quantity"] = df["quantity"].abs()
    log.add("order_items", "Negative quantity (sign error)", n, "Absolute value")

    disc = pd.to_numeric(df["discount"], errors="coerce")
    log.add("order_items", "Blank discount", disc.isna().sum(), "Set to 0")
    df["discount"] = disc.fillna(0.0)

    list_price = df["product_id"].map(products.set_index("product_id")["list_price"])
    too_high = df["unit_price"] > 10 * list_price
    df.loc[too_high, "unit_price"] = df.loc[too_high, "unit_price"] / 100
    log.add("order_items", "unit_price 100x list price (entered in paise)", too_high.sum(), "Divided by 100")

    n = df["unit_price"].isna().sum()
    df["unit_price"] = df["unit_price"].fillna(df.groupby("product_id")["unit_price"].transform("median"))
    log.add("order_items", "Missing unit_price", n, "Imputed product median price")
    return df


def run() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    raw = load_raw()
    log = QualityLog()
    clean = {
        "customers": clean_customers(raw["customers"], log),
        "orders": clean_orders(raw["orders"], log),
        "items": clean_items(raw["items"], raw["products"], log),
        "products": raw["products"],
    }
    # referential-integrity checks (should all be zero)
    o, i, c = clean["orders"], clean["items"], clean["customers"]
    log.add("checks", "Orders with unknown customer_id", (~o["customer_id"].isin(c["customer_id"])).sum(), "Assert 0")
    log.add("checks", "Order lines with unknown order_id", (~i["order_id"].isin(o["order_id"])).sum(), "Assert 0")
    log.add("checks", "Duplicate order_id after cleaning", o["order_id"].duplicated().sum(), "Assert 0")
    return clean, log.frame()
