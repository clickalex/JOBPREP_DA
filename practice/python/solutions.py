"""Reference solutions for practice/python/exercises.py.

Try the exercises first! There is usually more than one good way to solve
each one — check.py compares results, not code.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

VALID = ["Delivered", "Shipped"]
CITY_ALIASES = {"Bangalore": "Bengaluru", "New Delhi": "Delhi", "Bombay": "Mumbai",
                "Gurgaon": "Gurugram", "Calcutta": "Kolkata", "Madras": "Chennai"}
PAYMENT_MAP = {"cod": "Cash on Delivery", "cash on delivery": "Cash on Delivery", "upi": "UPI",
               "credit card": "Credit Card", "cc": "Credit Card", "debit card": "Debit Card",
               "dc": "Debit Card", "net banking": "Net Banking"}


def _valid_lines(orders, items):
    """Order lines of valid orders with a net_revenue column (+ order columns)."""
    lines = items.merge(orders[orders["status"].isin(VALID)], on="order_id", how="inner")
    lines["net_revenue"] = lines["quantity"] * lines["unit_price"] - lines["discount"]
    return lines


def _order_values(orders, items):
    lines = _valid_lines(orders, items)
    return lines.groupby("order_id", as_index=False).agg(
        device=("device", "first"), coupon_code=("coupon_code", "first"),
        customer_id=("customer_id", "first"), order_ts=("order_ts", "first"),
        order_value=("net_revenue", "sum"))


# ============================================================ A. Cleaning
def p01_count_duplicates(customers_raw):
    return int(customers_raw.duplicated().sum())


def p02_clean_city(city):
    s = city.str.strip().str.title()
    return s.replace(CITY_ALIASES)


def p03_parse_dates(dates):
    out = pd.Series(pd.NaT, index=dates.index, dtype="datetime64[ns]")
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"]:
        parsed = pd.to_datetime(dates, format=fmt, errors="coerce")
        out = out.fillna(parsed)
    return out
    # (pd.to_datetime(dates, format="mixed", dayfirst=True) also works in pandas >= 2.0)


def p04_clean_customers(customers_raw):
    df = customers_raw.copy()
    for col in ["first_name", "last_name"]:
        df[col] = df[col].str.strip()
    df["city"] = p02_clean_city(df["city"])
    df["email"] = df["email"].str.strip().str.lower()
    df["signup_date"] = p03_parse_dates(df["signup_date"])
    df["acquisition_channel"] = df["acquisition_channel"].fillna("Unknown")
    df = df.drop_duplicates(subset="customer_id", keep="first")
    return df.sort_values("customer_id").reset_index(drop=True)


def p05_clean_orders(orders_raw):
    df = orders_raw.drop_duplicates().copy()
    df["status"] = df["status"].str.strip().str.title()
    key = df["payment_method"].str.strip().str.lower()
    df["payment_method"] = key.map(PAYMENT_MAP).fillna(df["payment_method"])
    return df.sort_values("order_id").reset_index(drop=True)


def p06_clean_items(items_raw, products):
    df = items_raw.copy()
    df["quantity"] = df["quantity"].abs()
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
    list_price = df["product_id"].map(products.set_index("product_id")["list_price"])
    too_high = df["unit_price"] > 10 * list_price
    df.loc[too_high, "unit_price"] = df.loc[too_high, "unit_price"] / 100
    median_price = df.groupby("product_id")["unit_price"].transform("median")
    df["unit_price"] = df["unit_price"].fillna(median_price)
    return df


# ============================================================ B. Analysis
def p07_revenue_by_category(orders, items, products):
    lines = _valid_lines(orders, items).merge(products[["product_id", "category"]], on="product_id")
    out = lines.groupby("category", as_index=False)["net_revenue"].sum()
    return out.sort_values("net_revenue", ascending=False).reset_index(drop=True)


def p08_monthly_revenue(orders, items):
    lines = _valid_lines(orders, items)
    return lines.groupby(lines["order_ts"].dt.strftime("%Y-%m"))["net_revenue"].sum().sort_index()


def p09_top_customers(orders, items, customers, n=5):
    lines = _valid_lines(orders, items)
    rev = lines.groupby("customer_id", as_index=False)["net_revenue"].sum()
    rev = rev.merge(customers[["customer_id", "first_name", "last_name"]], on="customer_id")
    rev["customer_name"] = rev["first_name"] + " " + rev["last_name"]
    rev = rev.sort_values("net_revenue", ascending=False).head(n)
    return rev[["customer_id", "customer_name", "net_revenue"]].reset_index(drop=True)


def p10_aov_by_device(orders, items):
    ov = _order_values(orders, items)
    out = ov.groupby("device").agg(n_orders=("order_id", "count"), aov=("order_value", "mean"))
    return out.sort_values("aov", ascending=False).reset_index()


def p11_region_category_pivot(orders, items, products, customers):
    lines = (_valid_lines(orders, items)
             .merge(products[["product_id", "category"]], on="product_id")
             .merge(customers[["customer_id", "region"]], on="customer_id"))
    pv = lines.pivot_table(index="region", columns="category", values="net_revenue",
                           aggfunc="sum", fill_value=0)
    return pv.sort_index().sort_index(axis=1).round(0)


def p12_cancel_rate_by_payment(orders):
    rate = orders["status"].eq("Cancelled").groupby(orders["payment_method"]).mean() * 100
    return rate.round(1).sort_values(ascending=False)


def p13_order_count_buckets(orders):
    n = orders.groupby("customer_id").size()
    bucket = n.clip(upper=5).astype(str).replace({"5": "5+"})
    out = bucket.value_counts().rename_axis("orders_bucket").reset_index(name="n_customers")
    return out.sort_values("orders_bucket").reset_index(drop=True)


def p14_days_to_second_order(orders):
    o = orders.sort_values(["customer_id", "order_ts", "order_id"])
    o["n"] = o.groupby("customer_id").cumcount() + 1
    first = o[o["n"] == 1].set_index("customer_id")["order_ts"]
    second = o[o["n"] == 2].set_index("customer_id")["order_ts"]
    gap = (second - first.reindex(second.index)).dt.total_seconds() / 86400
    return round(float(gap.mean()), 1)


def p15_daily_orders_rolling(orders):
    oct_ = orders[(orders["order_ts"] >= "2025-10-01") & (orders["order_ts"] < "2025-11-01")]
    daily = oct_.set_index("order_ts").resample("D").size()
    daily = daily.reindex(pd.date_range("2025-10-01", "2025-10-31", freq="D"), fill_value=0)
    out = pd.DataFrame({"date": daily.index, "orders": daily.values})
    out["rolling_7d"] = out["orders"].rolling(7, min_periods=1).mean().round(2)
    return out


def p16_mom_growth(orders, items):
    m = p08_monthly_revenue(orders, items)
    out = pd.DataFrame({"month": m.index, "net_revenue": m.values})
    out["mom_pct"] = (out["net_revenue"].pct_change() * 100).round(1)
    return out


def p17_cohort_matrix(orders):
    o = orders[["customer_id", "order_ts"]].copy()
    o["order_month"] = o["order_ts"].dt.to_period("M")
    o["cohort"] = o.groupby("customer_id")["order_month"].transform("min")
    o["offset"] = (o["order_month"] - o["cohort"]).apply(lambda d: d.n)
    o = o[o["offset"].between(0, 6)]
    counts = o.groupby(["cohort", "offset"])["customer_id"].nunique().unstack(fill_value=0)
    pct = counts.div(counts[0], axis=0) * 100
    pct = pct.reindex(columns=range(7), fill_value=0).round(1)
    pct.index = pct.index.astype(str)
    return pct


def p18_funnel(sessions):
    steps = {"sessions": len(sessions), "viewed_product": sessions["viewed_product"].sum(),
             "added_to_cart": sessions["added_to_cart"].sum(), "began_checkout": sessions["began_checkout"].sum(),
             "purchased": sessions["purchased"].sum()}
    out = pd.DataFrame({"step": list(steps), "sessions": [int(v) for v in steps.values()]})
    out["pct_of_previous"] = (out["sessions"] / out["sessions"].shift(1) * 100).round(1)
    out["pct_of_total"] = (out["sessions"] / out["sessions"].iloc[0] * 100).round(1)
    return out


def p19_ab_test(experiment):
    g = experiment.groupby("variant")["converted"].agg(["sum", "count"])
    x_a, n_a = g.loc["A_control"]
    x_b, n_b = g.loc["B_new_checkout"]
    p_a, p_b = x_a / n_a, x_b / n_b
    p_pool = (x_a + x_b) / (n_a + n_b)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se_pool
    p_value = 2 * stats.norm.sf(abs(z))
    se_diff = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    return {"control_rate": round(p_a, 4), "treatment_rate": round(p_b, 4),
            "abs_lift": round(p_b - p_a, 4), "z": round(z, 2), "p_value": round(p_value, 4),
            "ci_low": round(p_b - p_a - 1.96 * se_diff, 4), "ci_high": round(p_b - p_a + 1.96 * se_diff, 4)}


def p20_ab_by_device(experiment):
    rows = []
    for device, sub in experiment.groupby("device"):
        r = p19_ab_test(sub)
        rows.append({"device": device, "control_rate": r["control_rate"], "treatment_rate": r["treatment_rate"],
                     "lift_pp": round(r["abs_lift"] * 100, 2), "p_value": r["p_value"]})
    return pd.DataFrame(rows).sort_values("device").reset_index(drop=True)


def p21_iqr_outliers(orders, items):
    v = _order_values(orders, items)["order_value"]
    q1, q3 = v.quantile([0.25, 0.75])
    return int((v > q3 + 1.5 * (q3 - q1)).sum())


def p22_coupon_ttest(orders, items):
    ov = _order_values(orders, items)
    a = ov.loc[ov["coupon_code"].notna(), "order_value"]
    b = ov.loc[ov["coupon_code"].isna(), "order_value"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return {"mean_coupon": round(a.mean(), 2), "mean_no_coupon": round(b.mean(), 2),
            "t_stat": round(t, 2), "p_value": round(p, 4)}


def p23_top_pairs(items, products, n=5):
    names = products.set_index("product_id")["product_name"]
    counts = {}
    for _, pids in items.groupby("order_id")["product_id"]:
        for a, b in combinations(sorted(set(pids)), 2):
            counts[(a, b)] = counts.get((a, b), 0) + 1
    out = pd.DataFrame([(names[a], names[b], c) for (a, b), c in counts.items()],
                       columns=["product_a", "product_b", "n_orders"])
    return (out.sort_values(["n_orders", "product_a", "product_b"], ascending=[False, True, True])
               .head(n).reset_index(drop=True))


def p24_org_levels(employees):
    mgr = employees.set_index("employee_id")["manager_id"]

    def level(eid):
        depth = 0
        while pd.notna(mgr[eid]):
            eid = int(mgr[eid])
            depth += 1
        return depth

    out = employees[["employee_id", "full_name"]].copy()
    out["level"] = out["employee_id"].map(level)
    return out.sort_values("employee_id").reset_index(drop=True)


def p25_channel_ltv(orders, items, customers):
    rev = _valid_lines(orders, items).groupby("customer_id")["net_revenue"].sum()
    c = customers[["customer_id", "acquisition_channel"]].copy()
    c["revenue"] = c["customer_id"].map(rev).fillna(0)
    c["is_buyer"] = c["revenue"] > 0
    out = c.groupby("acquisition_channel").agg(customers=("customer_id", "count"),
                                               buyer_pct=("is_buyer", "mean"),
                                               revenue_per_customer=("revenue", "mean"))
    out["buyer_pct"] = (out["buyer_pct"] * 100).round(1)
    out["revenue_per_customer"] = out["revenue_per_customer"].round(2)
    return out.sort_values("revenue_per_customer", ascending=False).reset_index()


# ==================================================== E. API ingestion
def _flatten(api_pages):
    rows = [r for page in api_pages for r in page["records"]]
    return pd.DataFrame(rows, columns=["event_id", "customer_id", "event_type", "event_ts", "amount"])


def p26_flatten_pages(api_pages):
    return _flatten(api_pages)


def p27_dedupe_and_tidy(api_pages):
    df = _flatten(api_pages).drop_duplicates(subset="event_id", keep="first").copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    return df.sort_values("event_id").reset_index(drop=True)


def p28_validation_report(api_pages):
    df = _flatten(api_pages)
    total = len(df)
    dupes = int(df.duplicated(subset="event_id", keep="first").sum())
    uniq = df.drop_duplicates(subset="event_id", keep="first").copy()
    amount = pd.to_numeric(uniq["amount"], errors="coerce")
    invalid = int(((amount.isna()) | (amount < 0)).sum())
    return {"total_records": total, "duplicate_ids": dupes,
            "invalid_amounts": invalid, "valid_records": len(uniq) - invalid}
