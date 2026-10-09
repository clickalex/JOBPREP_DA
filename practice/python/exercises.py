"""
Python / pandas practice — 28 exercises on the ShopKart data.

HOW TO USE
  1. Replace each `raise NotImplementedError` with your solution.
  2. Grade yourself from the repo root:
         python practice/python/check.py           # everything you've attempted
         python practice/python/check.py 4 17      # specific exercises
  3. Stuck? Reference answers live in solutions.py (try first!).

INPUTS — the checker passes fresh copies of these DataFrames by parameter name:
  customers_raw, orders_raw, items_raw   messy exports from data/raw (all read with pd.read_csv defaults)
  customers, products, orders, items,    clean tables from data/clean, with dates parsed to datetime64
  sessions, experiment, employees        (see data/README.md for the data dictionary)
  city, dates                            customers_raw["city"] / customers_raw["signup_date"] (p02, p03)
  api_pages                              cached pages of an events-API snapshot: list of
                                         {"page", "next_page", "records"} dicts (p26-p28)

CONVENTIONS (same as the SQL set)
  net line revenue = quantity * unit_price - discount
  valid order      = status in ("Delivered", "Shipped")
  Floats are compared to 2 decimals. Column NAMES don't matter; column order and
  count do. Row order matters only where the docstring says "sorted".
"""
from __future__ import annotations

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
from scipy import stats  # noqa: F401

VALID = ["Delivered", "Shipped"]


# =========================================================================== #
# A. DATA CLEANING  (the raw files)
# =========================================================================== #
def p01_count_duplicates(customers_raw: pd.DataFrame) -> int:
    """How many rows in customers_raw are EXACT duplicates of an earlier row?
    Return an int.  (DataFrame.duplicated)"""
    raise NotImplementedError


def p02_clean_city(city: pd.Series) -> pd.Series:
    """Standardise the raw `city` column:
      * strip whitespace and convert to Title Case  ('  NEW DELHI' -> 'New Delhi')
      * then map old/alternate names to the official ones:
        Bangalore->Bengaluru, New Delhi->Delhi, Bombay->Mumbai, Gurgaon->Gurugram,
        Calcutta->Kolkata, Madras->Chennai
    Return a Series with the same index."""
    raise NotImplementedError


def p03_parse_dates(dates: pd.Series) -> pd.Series:
    """`signup_date` in customers_raw mixes three formats: '2024-03-05', '05/03/2024'
    (day first!) and '05 Mar 2024'. Return a datetime64 Series with the same index."""
    raise NotImplementedError


def p04_clean_customers(customers_raw: pd.DataFrame) -> pd.DataFrame:
    """Produce an analysis-ready customer table. Keep the same columns, and:
      * strip whitespace from first_name and last_name
      * clean `city` (p02) and parse `signup_date` (p03)
      * lower-case and strip `email` (leave missing emails as NaN)
      * fill missing acquisition_channel with 'Unknown'
      * keep ONE row per customer_id (the first occurrence)
    Return sorted by customer_id with a fresh 0..n-1 index."""
    raise NotImplementedError


def p05_clean_orders(orders_raw: pd.DataFrame) -> pd.DataFrame:
    """Clean orders_raw:
      * drop exact duplicate rows
      * `status`: strip + Title Case ('delivered ' -> 'Delivered', 'CANCELLED' -> 'Cancelled')
      * `payment_method`: map every variant to one of
        'UPI', 'Credit Card', 'Debit Card', 'Cash on Delivery', 'Net Banking'
        (variants include 'upi', 'Upi', 'COD', 'cod', 'Cash On Delivery', 'CC', 'DC', 'credit card', ...)
    Return sorted by order_id with a fresh index, same columns."""
    raise NotImplementedError


def p06_clean_items(items_raw: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Fix the order lines, in this order:
      1. quantity: some are negative (sign error) -> make positive
      2. discount: blanks mean 0 -> numeric, NaN -> 0.0
      3. unit_price > 10 x the product's list_price was entered in paise -> divide by 100
      4. missing unit_price -> fill with the MEDIAN unit_price of that product_id (after step 3)
    Keep the original row order, index and columns."""
    raise NotImplementedError


# =========================================================================== #
# B. ANALYSIS  (clean tables)
# =========================================================================== #
def p07_revenue_by_category(orders, items, products) -> pd.DataFrame:
    """Net revenue of valid orders per category.
    Return DataFrame [category, net_revenue], sorted by net_revenue descending."""
    raise NotImplementedError


def p08_monthly_revenue(orders, items) -> pd.Series:
    """Net revenue of valid orders per month. Return a Series indexed by 'YYYY-MM'
    strings, sorted by month."""
    raise NotImplementedError


def p09_top_customers(orders, items, customers, n=5) -> pd.DataFrame:
    """Top-n customers by net revenue (valid orders).
    Return [customer_id, customer_name ('First Last'), net_revenue], sorted descending."""
    raise NotImplementedError


def p10_aov_by_device(orders, items) -> pd.DataFrame:
    """Average order value by device: first total each valid order's net revenue,
    then average per device. Return [device, n_orders, aov], sorted by aov descending."""
    raise NotImplementedError


def p11_region_category_pivot(orders, items, products, customers) -> pd.DataFrame:
    """Pivot table of valid net revenue: rows = customer region, columns = product category,
    values rounded to 0 decimals, missing combinations = 0. Sort rows and columns alphabetically."""
    raise NotImplementedError


def p12_cancel_rate_by_payment(orders) -> pd.Series:
    """% of orders with status 'Cancelled' per payment_method (1 dp).
    Return a Series indexed by payment_method, sorted by rate descending."""
    raise NotImplementedError


def p13_order_count_buckets(orders) -> pd.DataFrame:
    """How many customers placed 1, 2, 3, 4 and 5+ orders (any status)?
    Return [orders_bucket, n_customers] where orders_bucket is '1','2','3','4','5+', in that order."""
    raise NotImplementedError


def p14_days_to_second_order(orders) -> float:
    """For customers with 2+ orders (any status): mean days between 1st and 2nd order,
    using exact timestamps (fractional days). Order ties by order_id. Return float rounded to 1 dp."""
    raise NotImplementedError


def p15_daily_orders_rolling(orders) -> pd.DataFrame:
    """Daily order counts (any status) for October 2025, including days with zero orders,
    plus a trailing 7-day rolling mean (min_periods=1, 2 dp).
    Return [date, orders, rolling_7d] sorted by date (31 rows)."""
    raise NotImplementedError


def p16_mom_growth(orders, items) -> pd.DataFrame:
    """Monthly valid net revenue with month-over-month % change (1 dp, NaN for the first month).
    Return [month ('YYYY-MM'), net_revenue, mom_pct] sorted by month."""
    raise NotImplementedError


def p17_cohort_matrix(orders) -> pd.DataFrame:
    """Retention matrix. Cohort = month of a customer's first order (any status).
    Rows: cohort 'YYYY-MM' (sorted). Columns: 0..6 = months since first order.
    Values: % of the cohort that ordered in that month (1 dp; column 0 is 100.0).
    Fill combinations with no activity with 0."""
    raise NotImplementedError


def p18_funnel(sessions) -> pd.DataFrame:
    """Overall web funnel. Steps in order: sessions, viewed_product, added_to_cart,
    began_checkout, purchased. Return [step, sessions, pct_of_previous, pct_of_total]
    (pcts 1 dp; pct_of_previous is NaN for the first step)."""
    raise NotImplementedError


# =========================================================================== #
# C. STATISTICS & EXPERIMENTS
# =========================================================================== #
def p19_ab_test(experiment) -> dict:
    """Two-proportion z-test on `converted`, B_new_checkout vs A_control. Return a dict:
      control_rate, treatment_rate, abs_lift (B - A)       -> 4 dp
      z (POOLED standard error)                            -> 2 dp
      p_value (two-sided)                                  -> 4 dp
      ci_low, ci_high: 95% CI of the lift, UNPOOLED SE     -> 4 dp"""
    raise NotImplementedError


def p20_ab_by_device(experiment) -> pd.DataFrame:
    """Repeat p19 within each device. Return [device, control_rate, treatment_rate,
    lift_pp (percentage points, 2 dp), p_value] sorted by device name."""
    raise NotImplementedError


def p21_iqr_outliers(orders, items) -> int:
    """Compute each valid order's net value. How many orders are HIGH outliers by the
    1.5 x IQR rule (value > Q3 + 1.5*IQR)? Use pandas' default quantile interpolation."""
    raise NotImplementedError


def p22_coupon_ttest(orders, items) -> dict:
    """Do coupon orders have a different average order value? Using valid orders' net values,
    run a Welch t-test (unequal variances), coupon orders vs no-coupon orders. Return dict:
    mean_coupon, mean_no_coupon (2 dp), t_stat (2 dp), p_value (4 dp)."""
    raise NotImplementedError


# =========================================================================== #
# D. PUTTING IT TOGETHER
# =========================================================================== #
def p23_top_pairs(items, products, n=5) -> pd.DataFrame:
    """Products most often bought together (same order_id, any status). Count each unordered
    pair once, lower product_id as product_a. Return [product_a, product_b, n_orders] with
    product NAMES, top n by n_orders, ties broken by product_a then product_b name."""
    raise NotImplementedError


def p24_org_levels(employees) -> pd.DataFrame:
    """Depth of each employee in the org chart: CEO (no manager) = 0, their reports = 1, ...
    Return [employee_id, full_name, level] sorted by employee_id."""
    raise NotImplementedError


def p25_channel_ltv(orders, items, customers) -> pd.DataFrame:
    """Which acquisition channel brings the most valuable customers? For ALL customers
    (including those who never bought), per acquisition_channel:
      customers             count
      buyer_pct             % with any valid-order revenue (1 dp)
      revenue_per_customer  mean valid net revenue per customer, non-buyers count as 0 (2 dp)
    Return [acquisition_channel, customers, buyer_pct, revenue_per_customer]
    sorted by revenue_per_customer descending."""
    raise NotImplementedError


# =========================================================================== #
# E. API INGESTION  (cached JSON fixture — no live network calls)
# =========================================================================== #
def p26_flatten_pages(api_pages: list) -> pd.DataFrame:
    """api_pages is a list of page payloads from a cached events-API snapshot:
    {"page": int, "next_page": int | None, "records": [...]}.
    Concatenate the records of every page into ONE DataFrame, in page order
    (page 1 records first, then page 2, then page 3). Keep every row — duplicates,
    missing amounts and all. Return columns in the order they appear in the records
    (event_id, customer_id, event_type, event_ts, amount)."""
    raise NotImplementedError


def p27_dedupe_and_tidy(api_pages: list) -> pd.DataFrame:
    """Build an analysis-ready table from the same pages:
      1. flatten all pages (page order)
      2. drop duplicate event_ids, keeping the FIRST occurrence
      3. amount -> numeric (values that don't parse stay NaN; do not drop rows)
      4. event_ts -> datetime64
      5. sort by event_id and reset the index
    Return all 13 unique events."""
    raise NotImplementedError


def p28_validation_report(api_pages: list) -> dict:
    """Before analysing, report what the ingestion found. Return a dict with:
      total_records    all rows across every page
      duplicate_ids    rows removed when de-duplicating by event_id (keep first)
      invalid_amounts  unique events whose amount is missing, doesn't parse to a
                       number, or is negative
      valid_records    unique events left with a valid (non-negative numeric) amount"""
    raise NotImplementedError
