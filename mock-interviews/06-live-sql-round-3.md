# Mock 06 · Live SQL round 3: advanced SQL (45 minutes)

The hardest live round: window functions over aggregates, per-group medians, event sequences, rolling windows and the
most famous NULL trap in SQL. Try it after you're comfortable with [round 1](01-live-sql-round.md) and
[round 2](05-live-sql-round-2.md).

**Practising alone?** Use the playground's **timed mock mode**
([playground ▸ Round 3 ▸ ⏱ Start timed mock](https://clickalex.github.io/JOBPREP_DA/playground/#m14)).

**Interviewer:** read each prompt as written; give hints only after 2+ minutes of being stuck. Q1–Q4 in 35 minutes is a
strong performance at entry level.

> **Say this to open:** "Same ShopKart database. Revenue is quantity × unit_price − discount on Delivered or Shipped
> orders. Some of these are hard. I'm more interested in how you break them down than in perfect syntax."

---

## Q1 · Top category each month (≈7 min)

> "For each month of 2025, which category earned the most revenue, and what share of that month's revenue was it?"

**Looking for:** aggregate to month × category, then **two window functions over the aggregate**:
`SUM(revenue) OVER (PARTITION BY month)` for the share and `ROW_NUMBER()` for the winner.

- **Hint 1:** "Can you get both the month total and the category total in the same row without a second join?"
- **Hint 2:** "Top-N per group: what window function picks one row per partition?"
- **Follow-up:** "Fashion wins January and September. Why might that be?" (Look at category-level seasonality and
  promotions, e.g. end-of-season sales. Check whether Fashion grew or Electronics dipped in those months: the share
  alone can't tell you which.)

<details><summary>Answer key</summary>

```sql
WITH cat_month AS (
  SELECT strftime('%Y-%m', o.order_ts) AS month, p.category,
         SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p     ON p.product_id = oi.product_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
  GROUP BY month, p.category),
ranked AS (
  SELECT month, category, revenue,
         revenue / SUM(revenue) OVER (PARTITION BY month) AS share,
         ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC) AS rn
  FROM cat_month)
SELECT month, category AS top_category, ROUND(revenue, 2) AS revenue, ROUND(100.0 * share, 1) AS share_pct
FROM ranked WHERE rn = 1 ORDER BY month;
```

Electronics wins 10 of 12 months, with 32.9–42.0% share (peak: May at 42.0%). **Fashion** wins **January** (32.5%) and
**September** (32.7%).
</details>

## Q2 · AOV by order number (≈8 min)

> "Do customers spend more as they come back? Show average order value for customers' 1st, 2nd, 3rd, 4th and 5th-or-later
> valid orders."

**Looking for:** revenue per order first, then `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts)` to number
each customer's orders, then bucket and average.

- **Hint:** "How do you know whether an order is someone's 1st or 3rd?"
- **Follow-up:** "The 4th order has the highest AOV but '5+' drops. What's going on?" (Survivorship and small samples:
  only 510 fourth orders, and the 5+ bucket mixes very loyal customers' frequent small top-ups. Differences of ±₹100–300
  may be noise; check confidence intervals before telling a story.)

<details><summary>Answer key</summary>

```sql
WITH ov AS (
  SELECT o.order_id, o.customer_id, o.order_ts,
         SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
  GROUP BY o.order_id),
seq AS (
  SELECT revenue, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts, order_id) AS n FROM ov)
SELECT CASE WHEN n >= 5 THEN '5+' ELSE CAST(n AS TEXT) END AS order_number,
       COUNT(*) AS orders, ROUND(AVG(revenue), 2) AS aov
FROM seq GROUP BY order_number ORDER BY order_number;
```

| order # | orders | AOV (₹) |
|---|---:|---:|
| 1 | 5,680 | 2,956.57 |
| 2 | 2,451 | 3,078.11 |
| 3 | 1,034 | 3,051.93 |
| 4 | 510 | 3,328.76 |
| 5+ | 450 | 2,979.53 |
</details>

## Q3 · Median order value per device (≈10 min)

> "Give me the median order value for each device. SQLite has no MEDIAN function."

**Looking for:** per-group median with window functions: `ROW_NUMBER()` and `COUNT(*) OVER (PARTITION BY device)`,
keeping the middle row (odd count) or averaging the middle two (even count).

- **Hint 1:** "If you sort a group's orders and number them 1…n, which row numbers are the middle?"
- **Hint 2:** "`(n + 1) / 2` and `(n + 2) / 2` with integer division: what do they give for odd and even n?"
- **Follow-up:** "Why report the median here rather than the mean?" (Order values are right-skewed. A few large
  Electronics orders pull the mean (AOV ≈ ₹3,000) well above the typical order (≈ ₹2,300).)

<details><summary>Answer key</summary>

```sql
WITH ov AS (
  SELECT o.order_id, o.device, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
  GROUP BY o.order_id, o.device),
ranked AS (
  SELECT device, revenue,
         ROW_NUMBER() OVER (PARTITION BY device ORDER BY revenue) AS rn,
         COUNT(*)     OVER (PARTITION BY device) AS cnt
  FROM ov)
SELECT device, ROUND(AVG(revenue), 2) AS median_order_value
FROM ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY device
ORDER BY median_order_value DESC;
```

Mobile App **₹2,299.00**, Mobile Web ₹2,298.00, Desktop ₹2,230.40. The medians are almost identical: device doesn't
change what people spend, it changes *whether* they buy (see the funnel questions).
</details>

## Q4 · Sessions before the first purchase (≈8 min)

> "For logged-in customers who have made a purchase on the website, how many sessions did they have *before* their
> first purchasing session, on average? And what share bought in their very first session?"

**Looking for:** `MIN(CASE WHEN purchased = 1 THEN session_start END) OVER (PARTITION BY customer_id)` to stamp each
customer's first purchase time on every row, then count earlier sessions. Exclude anonymous sessions (NULL customer_id).

- **Hint:** "Can you attach each customer's first purchase time to all of their sessions without a self-join?"
- **Follow-up:** "What would you do with this number?" (Set retargeting and attribution windows: 36% buy on the first
  visit, the rest need about one more session on average. Dig into the sources of those first sessions.)

<details><summary>Answer key</summary>

**2,427 purchasers; 1.3 sessions before the first purchase on average; 35.8% bought in their first session.**

```sql
WITH s AS (
  SELECT customer_id, session_start, purchased,
         MIN(CASE WHEN purchased = 1 THEN session_start END) OVER (PARTITION BY customer_id) AS first_purchase_ts
  FROM web_sessions
  WHERE customer_id IS NOT NULL),
per_customer AS (
  SELECT customer_id, SUM(session_start < first_purchase_ts) AS sessions_before
  FROM s WHERE first_purchase_ts IS NOT NULL
  GROUP BY customer_id)
SELECT COUNT(*) AS purchasers,
       ROUND(AVG(sessions_before), 2) AS avg_sessions_before_first_purchase,
       ROUND(100.0 * SUM(sessions_before = 0) / COUNT(*), 1) AS pct_bought_first_session
FROM per_customer;
```
</details>

## Q5 · Best 7 days of the year (stretch, ≈8 min)

> "Which 7-day window in 2025 had the highest revenue? Give me the start date, end date and revenue."

**Looking for:** daily revenue, then `SUM(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`, and
`LAG(day, 6)` for the window start. Bonus if the candidate asks whether any day has zero orders, since `ROWS` counts
rows, not days (every 2025 day has orders, so it's safe here; otherwise build a date spine, as in SQL Q55).

- **Hint:** "What window frame clause gives you 'this row and the 6 before it'?"
- **Follow-up:** "What's the difference between ROWS and RANGE frames?" (ROWS counts physical rows; RANGE groups rows
  with equal ORDER BY values and, with numeric offsets, spans a value range. Missing days make ROWS-based "7-day"
  windows silently cover more than 7 days.)

<details><summary>Answer key</summary>

**2025-10-11 to 2025-10-17: ₹981,983.40**, right in the Diwali window (2025-10-05 to 10-25).

```sql
WITH daily AS (
  SELECT date(o.order_ts) AS day, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
  GROUP BY day),
rolling AS (
  SELECT day,
         LAG(day, 6) OVER (ORDER BY day) AS window_start,
         SUM(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7d
  FROM daily)
SELECT window_start, day AS window_end, ROUND(revenue_7d, 2) AS revenue_7d
FROM rolling
WHERE window_start IS NOT NULL
ORDER BY revenue_7d DESC
LIMIT 1;
```
</details>

## Q6 · Curveball: who manages nobody? (≈4 min)

> "List the employees who don't manage anyone."

**Looking for:** `NOT EXISTS` (or `NOT IN` with the NULLs filtered out). The famous trap:
`WHERE employee_id NOT IN (SELECT manager_id FROM employees)` returns **zero rows**, because the CEO's `manager_id` is
NULL and `x NOT IN (…, NULL)` is never true.

- **Hint:** "Run your query, then check: does the subquery return any NULLs?"
- **Follow-up:** "Explain exactly why NOT IN returned nothing." (`x NOT IN (a, b, NULL)` means `x <> a AND x <> b AND
  x <> NULL`. `x <> NULL` is UNKNOWN, so the whole condition is never TRUE. `NOT EXISTS` doesn't have this problem.)

<details><summary>Answer key</summary>

**19 employees** (the 11 managers are excluded). A candidate who gets 0 rows and says "nobody" has fallen into the trap.

```sql
SELECT e.full_name, e.department
FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.employee_id)
ORDER BY e.full_name;
```
</details>

---

## Interviewer scorecard

| | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 |
|---|---|---|---|---|---|---|
| Minutes taken | | | | | | |
| Correct? (Y / after hint / N) | | | | | | |
| Explained reasoning? | | | | | | |

Score the five rubric dimensions from the [mock-interview README](README.md#universal-scoring-rubric-14-per-dimension).
**Pass signal:** Q1–Q4 correct within 35 minutes with at most two hints.
