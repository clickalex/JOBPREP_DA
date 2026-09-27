# 04 · Python & pandas for data analysts

Python rounds for DA roles are usually **pandas-focused**: load a CSV, clean it, answer business questions and make a
chart, often in a Jupyter or Colab notebook shared on screen, or as a take-home. LeetCode-style algorithms are rare for
analyst roles. Basic Python (lists, dicts, loops, functions) is still expected.

**Practice:** [25 graded exercises](../practice/python/exercises.py) · `python practice/python/check.py`

---

## 1. Python basics they still check

```python
nums = [3, 1, 4, 1, 5]
squares = [n ** 2 for n in nums if n > 1]           # list comprehension
counts = {}
for n in nums:
    counts[n] = counts.get(n, 0) + 1               # frequency dict  (or collections.Counter(nums))
top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
unique = set(nums)                                  # de-duplicate
first, *rest = nums                                 # unpacking
def pct(a, b=1):                                    # default args; guard against /0
    return 100 * a / b if b else None
```
Know: mutable vs immutable (list vs tuple), `is` vs `==`, `try/except`, f-strings, `enumerate`, `zip`.

## 2. SQL → pandas translation

| SQL | pandas |
|---|---|
| `SELECT a, b FROM t` | `t[["a", "b"]]` |
| `WHERE x > 5 AND y = 'A'` | `t[(t.x > 5) & (t.y == "A")]` or `t.query("x > 5 and y == 'A'")` |
| `WHERE y IN ('A','B')` | `t[t.y.isin(["A", "B"])]` |
| `WHERE col IS NULL` | `t[t.col.isna()]` |
| `ORDER BY x DESC LIMIT 5` | `t.sort_values("x", ascending=False).head(5)` or `t.nlargest(5, "x")` |
| `SELECT DISTINCT y` | `t.y.unique()` / `t.drop_duplicates("y")` |
| `COUNT(DISTINCT y)` | `t.y.nunique()` |
| `GROUP BY g` + aggregates | `t.groupby("g").agg(n=("id", "count"), rev=("rev", "sum"))` |
| `HAVING SUM(rev) > 100` | `...agg(...).query("rev > 100")` |
| `JOIN ... ON` | `a.merge(b, on="key", how="inner" / "left" / "outer")` |
| `UNION ALL` | `pd.concat([a, b])` |
| `CASE WHEN` | `np.where(cond, x, y)` / `np.select([c1, c2], [v1, v2], default)` / `pd.cut` |
| `ROW_NUMBER() OVER (PARTITION BY g ORDER BY d)` | `t.sort_values("d").groupby("g").cumcount() + 1` |
| `RANK() OVER (...)` | `t.groupby("g")["x"].rank(method="min", ascending=False)` |
| `LAG(x) OVER (PARTITION BY g ORDER BY d)` | `t.sort_values("d").groupby("g")["x"].shift(1)` |
| `SUM(x) OVER (PARTITION BY g)` | `t.groupby("g")["x"].transform("sum")` |
| running total | `t.groupby("g")["x"].cumsum()` |
| moving average | `t["x"].rolling(3).mean()` |

## 3. Cleaning recipes

```python
df = pd.read_csv("data/raw/orders_raw.csv")
df.info(); df.describe(include="all"); df.isna().sum(); df.duplicated().sum()   # always start here

df = df.drop_duplicates()
df["status"] = df["status"].str.strip().str.title()
df["payment_method"] = df["payment_method"].str.strip().str.lower().map(mapping).fillna(df["payment_method"])
df["order_ts"] = pd.to_datetime(df["order_ts"])                           # errors="coerce" turns bad values into NaT
df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0)
df["unit_price"] = df["unit_price"].fillna(df.groupby("product_id")["unit_price"].transform("median"))
df = df.astype({"customer_id": "int64", "device": "category"})
```

**Mixed date formats:** parse each known format explicitly and combine with `fillna` (see `p03`), or
`pd.to_datetime(s, format="mixed", dayfirst=True)` in pandas 2. **Never let pandas guess day vs month on Indian (DD/MM) data.**

**Missing values: decide, don't default.** Drop (if few and random), impute (median by group), flag (`is_missing` column),
or leave as NaN (if they genuinely mean "unknown"). **Say which one you chose and why.**

**Outliers:** investigate first (data error vs real VIP customer). Fix obvious unit errors, cap (winsorise), or analyse with the median.

## 4. groupby, merge, pivot, reshape

```python
# multiple named aggregations
summary = (lines.groupby(["region", "category"], as_index=False)
                .agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique"), avg_qty=("quantity", "mean")))

# per-row group metric (keeps shape), e.g. share of the customer's total
lines["share"] = lines["net_revenue"] / lines.groupby("customer_id")["net_revenue"].transform("sum")

# pivot
pv = lines.pivot_table(index="region", columns="category", values="net_revenue", aggfunc="sum", fill_value=0, margins=True)

# wide → long, long → wide
long = wide.melt(id_vars="month", var_name="category", value_name="revenue")
wide = long.pivot(index="month", columns="category", values="revenue")

# merge safely
m = orders.merge(customers, on="customer_id", how="left", validate="many_to_one", indicator=True)
m["_merge"].value_counts()      # rows that didn't match
```

⚠️ **Merge explosion:** duplicate keys on both sides multiply rows. `validate=` catches it; always compare `len()` before and after.

## 5. Time series

```python
s = orders.set_index("order_ts")
daily   = s.resample("D").size()                         # counts per day (fills missing days with 0)
monthly = s.resample("MS")["order_id"].count()           # month start
orders["month"] = orders["order_ts"].dt.to_period("M")   # or .dt.strftime("%Y-%m")
orders["weekday"] = orders["order_ts"].dt.day_name()
daily.rolling(7).mean()                                   # 7-day moving average
monthly.pct_change() * 100                                # MoM %
monthly.shift(12)                                         # same month last year (for YoY)
```

## 6. Visualisation (matplotlib / seaborn)

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 4))
monthly.plot(ax=ax, marker="o")
ax.set_title("Revenue doubled YoY; Diwali drives the October peak")   # insight as the title
ax.set_ylabel("₹"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("chart.png", dpi=150)
```
Seaborn one-liners: `sns.histplot`, `sns.boxplot(x=, y=)`, `sns.barplot`, `sns.heatmap(pivot, annot=True)`, `sns.lineplot(hue=)`.

## 7. Common gotchas

* **SettingWithCopyWarning:** you modified a slice. Use `.loc[row_mask, "col"] = value` on the original, or `.copy()` the subset.
* `and` / `or` don't work on Series. Use `&`, `|`, `~` **with parentheses**: `(a > 1) & (b < 2)`.
* `df.groupby(...)["x"].mean()` returns a Series with the group as index; add `.reset_index()` or `as_index=False`.
* `NaN != NaN`. Use `.isna()`. And `sum()` of an all-NaN column is 0 while `mean()` is NaN.
* Avoid `iterrows()` loops over big frames; vectorise with column operations, `np.where`, `map` or `merge`.
* `inplace=True` is discouraged; assign the result instead.

## 8. Interview questions

<details><summary><b><code>loc</code> vs <code>iloc</code>?</b></summary><code>loc</code> selects by label (and boolean masks), and label slices are end-inclusive; <code>iloc</code> selects by integer position, and slices are end-exclusive.</details>
<details><summary><b><code>apply</code> vs <code>map</code> vs <code>transform</code>?</b></summary><code>Series.map</code> maps values with a dict/function; <code>apply</code> runs a function per row/column/group (flexible, slow); <code>groupby().transform</code> returns a result the same shape as the input, which is great for adding group-level columns.</details>
<details><summary><b><code>merge</code> vs <code>join</code> vs <code>concat</code>?</b></summary><code>merge</code> is the SQL-style join on columns; <code>join</code> is a convenience method that joins on the index; <code>concat</code> stacks frames vertically (UNION) or side-by-side.</details>
<details><summary><b>How do you find and handle duplicates?</b></summary><code>df.duplicated(subset=[...], keep=False)</code> to inspect, then <code>drop_duplicates(subset, keep="first"/"last")</code>. Decide which record wins (e.g. latest update) and document it.</details>
<details><summary><b>How would you process a CSV too big for memory?</b></summary><code>read_csv(chunksize=...)</code> and aggregate per chunk; read only the needed <code>usecols</code> with compact <code>dtype</code>s (category, int32); use Parquet; or push the work to SQL / DuckDB / Polars.</details>
<details><summary><b>What's the difference between a list and a NumPy array?</b></summary>Lists hold any mix of types and are slow for maths; arrays are fixed-type, contiguous and vectorised (fast element-wise operations, broadcasting).</details>
