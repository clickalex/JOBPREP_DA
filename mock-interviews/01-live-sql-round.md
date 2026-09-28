# Mock 01 · Live SQL round (45 minutes)

**Setup:** the candidate shares a screen with a SQL editor open on `data/shopkart.db`. The
[SQL Playground](https://clickalex.github.io/JOBPREP_DA/playground/) (Scratchpad mode) works with zero setup. These
questions are **not** in the 60 practice exercises, so they're fresh even if you've done the whole set.

**Practising alone?** Open the playground's **timed mock mode**
([playground ▸ ⏱ Start timed mock](https://clickalex.github.io/JOBPREP_DA/playground/#m1)). It serves these same
questions against a 45-minute clock, grades your queries, reveals the hints below one at a time, asks the
follow-ups after each solve, and ends with a scorecard.

**Interviewer:** read the prompt as written. Give hints only when the candidate has been stuck for 2+ minutes, one
hint at a time. Aim for Q1–Q4 in the first 30 minutes; Q5–Q7 are stretch goals. Note the time each question takes.

> **Say this to open:** "We have an e-commerce company, ShopKart. Tables: customers, products, orders, order_items,
> web_sessions, employees. Revenue means quantity × unit_price − discount, counted only for orders with status
> Delivered or Shipped. Please think out loud; I care about your reasoning as much as the answer."

---

## Q1 · Warm-up (≈5 min)

> "How many distinct customers placed at least one valid order in 2025?"

**Looking for:** `COUNT(DISTINCT …)`, the status filter, and a half-open date range (`>= '2025-01-01' AND < '2026-01-01'`).

- **Hint:** "What does 'valid' mean here? How are timestamps stored?"
- **Follow-up:** "Why not `strftime('%Y', order_ts) = '2025'`?" (It works, but it can't use the index on `order_ts`.
  Range filters are sargable.)

<details><summary>Answer key</summary>

**4,033 customers.**

```sql
SELECT COUNT(DISTINCT customer_id) AS active_customers
FROM orders
WHERE status IN ('Delivered','Shipped')
  AND order_ts >= '2025-01-01' AND order_ts < '2026-01-01';
```
Common miss: forgetting `DISTINCT` gives the order count (6,541) instead.
</details>

## Q2 · Month-over-month growth (≈8 min)

> "Show 2025 revenue by month, plus the percentage change versus the previous month."

**Looking for:** aggregate first (in a CTE), *then* apply `LAG()` to the monthly totals. Avoid dividing integers.

- **Hint:** "Can a window function run over the result of a GROUP BY? How would you structure that?"
- **Follow-up 1:** "October is +107% and November −50%. Is something broken?" (No: Diwali fell on 2025-10-05..10-25.
  Seasonality means YoY or same-period comparisons beat MoM here.)
- **Follow-up 2:** "What does January's `mom_pct` show and why?" (NULL: there's no previous row inside 2025.)

<details><summary>Answer key</summary>

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', o.order_ts) AS month,
         SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
  GROUP BY 1)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_pct
FROM monthly ORDER BY month;
```

| month | revenue | mom_pct |
|---|---:|---:|
| 2025-01 | 1,138,689.35 | NULL |
| 2025-02 | 1,019,542.50 | −10.5 |
| 2025-03 | 1,314,976.55 | 29.0 |
| 2025-04 | 1,434,515.25 | 9.1 |
| 2025-05 | 1,680,767.90 | 17.2 |
| 2025-06 | 1,462,084.30 | −13.0 |
| 2025-07 | 1,589,079.10 | 8.7 |
| 2025-08 | 1,915,536.25 | 20.5 |
| 2025-09 | 1,584,978.65 | −17.3 |
| 2025-10 | 3,276,468.80 | 106.7 |
| 2025-11 | 1,655,441.20 | −49.5 |
| 2025-12 | 1,888,694.80 | 14.1 |
</details>

## Q3 · Channel quality (≈10 min)

> "Marketing wants to know which acquisition channel brings the best customers. For each channel, show the number of
> customers, the percentage who ever placed a valid order, and the average value of their first valid order."

**Looking for:** a `ROW_NUMBER()` to find each customer's first order, a `LEFT JOIN` from customers (so non-buyers
count in the denominator), and `COUNT(column)` vs `COUNT(*)` to get the conversion share.

- **Hint 1:** "How would you identify each customer's first order?"
- **Hint 2:** "If you INNER JOIN customers to orders, what happens to people who never bought?"
- **Follow-up:** "Paid Search has the highest first-order value. Is it the best channel?" (Not necessarily: Referral
  converts 83% vs Paid Social's 60%, and the portfolio project shows Referral's revenue per sign-up is ₹6,009 vs ₹2,520.
  First-order value alone ignores conversion and repeat behaviour, and the channels' costs.)

<details><summary>Answer key</summary>

```sql
WITH first_orders AS (
  SELECT o.customer_id, o.order_id,
         ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_ts, o.order_id) AS rn
  FROM orders o WHERE o.status IN ('Delivered','Shipped')),
fo_value AS (
  SELECT f.customer_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS first_value
  FROM first_orders f JOIN order_items oi ON oi.order_id = f.order_id
  WHERE f.rn = 1 GROUP BY f.customer_id)
SELECT c.acquisition_channel,
       COUNT(*) AS customers,
       ROUND(100.0 * COUNT(fv.customer_id) / COUNT(*), 1) AS pct_with_valid_order,
       ROUND(AVG(fv.first_value), 0) AS avg_first_order_value
FROM customers c LEFT JOIN fo_value fv ON fv.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY avg_first_order_value DESC;
```

| channel | customers | % with valid order | avg first order (₹) |
|---|---:|---:|---:|
| Paid Search | 1,528 | 71.1 | 3,058 |
| Organic Search | 2,227 | 74.8 | 3,007 |
| Affiliate | 667 | 62.5 | 2,976 |
| Email | 654 | 78.9 | 2,968 |
| Referral | 1,001 | 83.2 | 2,880 |
| Paid Social | 1,923 | 60.4 | 2,832 |
</details>

## Q4 · Top product per category (≈7 min)

> "For 2025, what was the single highest-revenue product in each category?"

**Looking for:** the classic "top-N per group" pattern with `ROW_NUMBER()` (or `RANK()` with a note about ties) in a
CTE, filtered in the outer query. Filtering on a window function in `WHERE` at the same level is an error.

- **Follow-up:** "How would your query change for the top 3? What if two products tie?" (`rn <= 3`; `RANK`/`DENSE_RANK`
  keeps ties, `ROW_NUMBER` breaks them arbitrarily unless you add a tiebreaker.)

<details><summary>Answer key</summary>

```sql
WITH prod AS (
  SELECT p.category, p.product_name, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
  GROUP BY p.category, p.product_name),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn FROM prod)
SELECT category, product_name, ROUND(revenue, 2) AS revenue
FROM ranked WHERE rn = 1 ORDER BY revenue DESC;
```

| category | product | revenue (₹) |
|---|---|---:|
| Electronics | Smartwatch | 1,703,822.30 |
| Fashion | Running Sneakers | 1,337,152.05 |
| Home & Kitchen | Mixer Grinder | 1,128,477.30 |
| Beauty | Perfume 100ml | 456,614.35 |
| Sports | Adjustable Dumbbells | 454,894.40 |
| Books | Competitive Exam Guide | 131,019.85 |
</details>

## Q5 · Time to second order (stretch, ≈8 min)

> "Of customers who made at least two valid orders, what share placed the second one within 30 days of the first?
> Also give the average gap."

**Looking for:** number the orders, then self-join order 1 to order 2 (or use `LEAD()`), and use `julianday()` for the
day difference. `SUM(condition)` counts true rows in SQLite.

- **Follow-up:** "Why does this matter to the business?" (It's the window for a post-purchase nudge. 31.7% come back
  within a month, so a day-7–21 email or offer targets the gap before customers lapse.)

<details><summary>Answer key</summary>

**2,451 repeat customers; 776 (31.7%) within 30 days; average gap 85.5 days.**

```sql
WITH seq AS (
  SELECT customer_id, order_ts,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts, order_id) AS rn
  FROM orders WHERE status IN ('Delivered','Shipped')),
pairs AS (
  SELECT f.customer_id, julianday(s.order_ts) - julianday(f.order_ts) AS gap_days
  FROM seq f JOIN seq s ON s.customer_id = f.customer_id AND f.rn = 1 AND s.rn = 2)
SELECT COUNT(*) AS repeat_customers,
       SUM(gap_days <= 30) AS within_30d,
       ROUND(100.0 * SUM(gap_days <= 30) / COUNT(*), 1) AS pct_within_30d,
       ROUND(AVG(gap_days), 1) AS avg_gap_days
FROM pairs;
```
</details>

## Q6 · Funnel by traffic source (stretch, ≈6 min)

> "Using web_sessions, compare traffic sources on each funnel step: view → cart → checkout → purchase. Where does Paid
> Social lose people?"

**Looking for:** step-to-step rates (each step divided by the previous one), not just overall conversion.

<details><summary>Answer key</summary>

```sql
SELECT traffic_source, COUNT(*) AS sessions,
       ROUND(100.0 * SUM(added_to_cart)  / SUM(viewed_product), 1) AS view_to_cart_pct,
       ROUND(100.0 * SUM(began_checkout) / SUM(added_to_cart),  1) AS cart_to_checkout_pct,
       ROUND(100.0 * SUM(purchased)      / SUM(began_checkout), 1) AS checkout_to_purchase_pct,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2) AS session_cvr_pct
FROM web_sessions GROUP BY traffic_source ORDER BY session_cvr_pct DESC;
```

| source | sessions | view→cart | cart→checkout | checkout→purchase | session CVR |
|---|---:|---:|---:|---:|---:|
| Email | 3,151 | 40.1 | 74.6 | 79.5 | 19.11 |
| Direct | 4,800 | 39.6 | 72.7 | 76.6 | 17.15 |
| Referral | 2,727 | 36.0 | 67.6 | 74.2 | 13.20 |
| Paid Search | 7,340 | 35.1 | 64.1 | 70.6 | 11.17 |
| Organic Search | 11,981 | 33.7 | 61.4 | 68.4 | 9.47 |
| Paid Social | 10,001 | 26.4 | 49.2 | 51.5 | 3.69 |

Paid Social is weakest at **every** step, but the gap widens further down the funnel (checkout→purchase is 51.5% vs
68–80% elsewhere). That points to low-intent traffic, not a single broken page.
</details>

## Q7 · Curveball: self-join (≈3 min)

> "List employees who earn more than their manager."

**Looking for:** a self-join `employees e JOIN employees m ON m.employee_id = e.manager_id`, and a calm,
verified reaction to whatever the result turns out to be.

<details><summary>Answer key</summary>

**Zero rows, and that's the correct answer.** Strong candidates don't panic or "fix" the query until it returns
something. They verify it instead: check that the join produces rows without the `WHERE` (it does: 29 employees have
managers), then say "no employee out-earns their manager in this data."

```sql
SELECT e.full_name AS employee, e.monthly_salary, m.full_name AS manager, m.monthly_salary AS manager_salary
FROM employees e JOIN employees m ON m.employee_id = e.manager_id
WHERE e.monthly_salary > m.monthly_salary;
```
</details>

---

## Interviewer scorecard

| | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 |
|---|---|---|---|---|---|---|---|
| Minutes taken | | | | | | | |
| Correct? (Y / after hint / N) | | | | | | | |
| Explained reasoning? | | | | | | | |

Then score the five rubric dimensions from the [mock-interview README](README.md#universal-scoring-rubric-14-per-dimension).
**Pass signal:** Q1–Q4 correct within 30–35 min with at most two hints, plus clear narration.
