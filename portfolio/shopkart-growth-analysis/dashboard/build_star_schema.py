"""
Export a star schema for Power BI / Tableau + a static preview of the dashboard.

    python portfolio/shopkart-growth-analysis/dashboard/build_star_schema.py

Writes dashboard/model/*.csv:
    fact_sales.csv     one row per order line (grain = order_item_id)
    dim_customer.csv   dim_product.csv   dim_date.csv (continuous calendar, Indian FY)
and dashboard/dashboard_preview.png (a mock-up of the Executive Overview page).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

# Windows consoles/pipes default to cp1252, which can't print ✓ ✗ ₹ — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
CLEAN = HERE.parents[2] / "data" / "clean"
OUT = HERE / "model"
OUT.mkdir(exist_ok=True)

orders = pd.read_csv(CLEAN / "orders.csv", parse_dates=["order_ts"])
items = pd.read_csv(CLEAN / "order_items.csv")
customers = pd.read_csv(CLEAN / "customers.csv", parse_dates=["signup_date"])
products = pd.read_csv(CLEAN / "products.csv")

# ---------------------------------------------------------------- fact
fact = items.merge(orders, on="order_id")
fact["date_key"] = fact["order_ts"].dt.strftime("%Y%m%d").astype(int)
fact["gross_amount"] = fact["quantity"] * fact["unit_price"]
fact["net_revenue"] = fact["gross_amount"] - fact["discount"]
fact = fact.merge(products[["product_id", "unit_cost"]], on="product_id")
fact["cogs"] = fact["quantity"] * fact["unit_cost"]
fact["is_valid"] = fact["status"].isin(["Delivered", "Shipped"]).astype(int)
first = orders.groupby("customer_id")["order_ts"].min()
fact["is_first_order"] = (fact["order_ts"] == fact["customer_id"].map(first)).astype(int)
fact = fact[["order_item_id", "order_id", "date_key", "customer_id", "product_id", "status", "payment_method",
             "device", "coupon_code", "quantity", "unit_price", "gross_amount", "discount", "net_revenue", "cogs",
             "shipping_fee", "is_valid", "is_first_order"]]
fact.to_csv(OUT / "fact_sales.csv", index=False, lineterminator="\n")

# ---------------------------------------------------------------- dims
dim_c = customers.drop(columns=["email", "first_name", "last_name"]).copy()
dim_c["age_band"] = pd.cut(2025 - dim_c["birth_year"], [0, 24, 34, 44, 120], labels=["18-24", "25-34", "35-44", "45+"])
dim_c["first_order_date"] = dim_c["customer_id"].map(first).dt.date
dim_c["cohort_month"] = dim_c["customer_id"].map(first).dt.strftime("%Y-%m")
dim_c.to_csv(OUT / "dim_customer.csv", index=False, lineterminator="\n")
products.to_csv(OUT / "dim_product.csv", index=False, lineterminator="\n")

dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
fy_start = np.where(dates.month >= 4, dates.year, dates.year - 1)
dim_d = pd.DataFrame({
    "date_key": dates.strftime("%Y%m%d").astype(int), "date": dates.date,
    "year": dates.year, "quarter": "Q" + dates.quarter.astype(str), "month_num": dates.month,
    "month_name": dates.strftime("%b"), "year_month": dates.strftime("%Y-%m"),
    "week_start": (dates - pd.to_timedelta(dates.weekday, unit="D")).date,
    "weekday_name": dates.strftime("%a"), "weekday_num": dates.weekday + 1,
    "is_weekend": (dates.weekday >= 5).astype(int),
    "fiscal_year": ["FY" + str(y + 1)[2:] for y in fy_start],           # Indian FY: Apr–Mar, FY26 = Apr 2025–Mar 2026
    "is_festive_season": (((dates >= "2024-10-15") & (dates <= "2024-11-05")) |
                          ((dates >= "2025-10-05") & (dates <= "2025-10-25"))).astype(int),
})
dim_d.to_csv(OUT / "dim_date.csv", index=False, lineterminator="\n")

# ---------------------------------------------------------------- preview mock-up
v = fact[fact.is_valid == 1].merge(dim_d[["date_key", "year_month", "year"]], on="date_key") \
                            .merge(products[["product_id", "category"]], on="product_id") \
                            .merge(dim_c[["customer_id", "region"]], on="customer_id")
v25 = v[v.year == 2025]
v24 = v[v.year == 2024]
rev25, rev24 = v25.net_revenue.sum(), v24.net_revenue.sum()
ord25, ord24 = v25.order_id.nunique(), v24.order_id.nunique()
o25 = fact.merge(dim_d[["date_key", "year"]], on="date_key").query("year == 2025")
ret25 = o25.drop_duplicates("order_id").status.eq("Returned").mean()
o24 = fact.merge(dim_d[["date_key", "year"]], on="date_key").query("year == 2024")
ret24 = o24.drop_duplicates("order_id").status.eq("Returned").mean()

fig = plt.figure(figsize=(14, 8), facecolor="#F4F6FA")
fig.text(0.02, 0.955, "ShopKart · Executive Overview", fontsize=18, fontweight="bold", color="#1F3864")
fig.text(0.02, 0.925, "Calendar 2025 vs 2024  ·  valid orders (Delivered + Shipped)  ·  slicers: Year · Region · Category · Device",
         fontsize=10, color="#595959")
cards = [("Net Revenue", f"₹{rev25/1e7:.2f} Cr", rev25 / rev24 - 1),
         ("Orders", f"{ord25:,}", ord25 / ord24 - 1),
         ("AOV", f"₹{rev25/ord25:,.0f}", (rev25 / ord25) / (rev24 / ord24) - 1),
         ("Return rate", f"{ret25:.1%}", ret25 - ret24)]
for i, (label, val, delta) in enumerate(cards):
    ax = fig.add_axes([0.02 + i * 0.245, 0.76, 0.225, 0.14])
    ax.set_facecolor("white"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#D9D9D9")
    ax.text(0.06, 0.72, label, fontsize=11, color="#595959", transform=ax.transAxes)
    ax.text(0.06, 0.28, val, fontsize=22, fontweight="bold", color="#1F3864", transform=ax.transAxes)
    good = delta >= 0 if label != "Return rate" else delta <= 0
    txt = f"{delta:+.1%} YoY" if label != "Return rate" else f"{delta*100:+.1f} pp YoY"
    ax.text(0.94, 0.3, txt, fontsize=11, ha="right", color="#2CA02C" if good else "#D62728", transform=ax.transAxes)

m = v.groupby("year_month").net_revenue.sum()
ax = fig.add_axes([0.05, 0.40, 0.56, 0.30]); ax.set_facecolor("white")
ax.bar(range(len(m)), m.values, color=["#FF7F0E" if s[-2:] in ("10", "11") else "#1F77B4" for s in m.index])
ax.set_xticks(range(0, len(m), 3), m.index[::3], fontsize=8)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))
ax.set_title("Net revenue by month", loc="left", fontsize=11, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)

c = v25.groupby("category").net_revenue.sum().sort_values()
ax = fig.add_axes([0.72, 0.40, 0.26, 0.30]); ax.set_facecolor("white")
ax.barh(c.index, c.values, color="#1F77B4")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))
ax.set_title("2025 revenue by category", loc="left", fontsize=11, fontweight="bold")
ax.tick_params(labelsize=8); ax.spines[["top", "right"]].set_visible(False)

r = v25.groupby("region").net_revenue.sum().sort_values(ascending=False)
ax = fig.add_axes([0.05, 0.06, 0.40, 0.26]); ax.set_facecolor("white")
ax.bar(r.index, r.values, color="#2CA02C")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))
ax.set_title("2025 revenue by region", loc="left", fontsize=11, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)

d = o25.drop_duplicates("order_id").groupby("payment_method").status.apply(lambda s: s.eq("Cancelled").mean()).sort_values()
ax = fig.add_axes([0.56, 0.06, 0.42, 0.26]); ax.set_facecolor("white")
ax.barh(d.index, d.values * 100, color=["#D62728" if x == d.max() else "#9E9E9E" for x in d.values])
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("2025 cancellation rate by payment method", loc="left", fontsize=11, fontweight="bold")
ax.tick_params(labelsize=8); ax.spines[["top", "right"]].set_visible(False)
fig.savefig(HERE / "dashboard_preview.png", dpi=110, facecolor=fig.get_facecolor())

print(f"fact_sales {len(fact):,} rows · dim_customer {len(dim_c):,} · dim_product {len(products)} · dim_date {len(dim_d)}")
print(f"KPI check 2025: revenue ₹{rev25:,.2f} · orders {ord25:,} · AOV ₹{rev25/ord25:,.2f} · return rate {ret25:.2%}")
