# Mock 05 · Live SQL round 2: product & marketing analytics (45 minutes)

A second live SQL round with a product/marketing flavour: coupons, AOV, cohort value, basket size, churn and a classic
double-counting trap. None of these questions are in the 60 practice exercises or in [round 1](01-live-sql-round.md).

**Practising alone?** Use the playground's **timed mock mode**
([playground ▸ Round 2 ▸ ⏱ Start timed mock](https://clickalex.github.io/JOBPREP_DA/playground/#m8)). It grades each
query, reveals the hints one at a time, asks the follow-ups after each solve, and ends with a scorecard.

**Interviewer:** read each prompt as written; give hints only after 2+ minutes of being stuck. Aim for Q1–Q4 in the
first 30–35 minutes.

> **Say this to open:** "ShopKart is an e-commerce company. Revenue means quantity × unit_price − discount, counted only
> for orders with status Delivered or Shipped. Think out loud, and tell me your assumptions."

---

## Q1 · Coupon mix (≈5 min)

> "What share of 2025 valid orders used each coupon code? Treat orders without a coupon as their own group."

**Looking for:** `COALESCE` to label NULLs, and a share of total, either with a window function
(`SUM(COUNT(*)) OVER ()`) or a scalar subquery.

- **Hint:** "What does `GROUP BY coupon_code` do with orders that have no coupon?"
- **Follow-up:** "A third of orders use a coupon. Is that a problem?" (It depends on whether coupons create incremental
  orders or just discount orders that would have happened anyway. The coupon take-home and SQL Q40 suggest WELCOME15
  doesn't improve repeat rates, so it's worth testing with a holdout.)

<details><summary>Answer key</summary>

```sql
SELECT COALESCE(coupon_code, 'No coupon') AS coupon,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders
FROM orders
WHERE status IN ('Delivered','Shipped')
  AND order_ts >= '2025-01-01' AND order_ts < '2026-01-01'
GROUP BY coupon
ORDER BY orders DESC;
```

| coupon | orders | % of orders |
|---|---:|---:|
| No coupon | 4,345 | 66.4 |
| WELCOME15 | 1,417 | 21.7 |
| FEST10 | 408 | 6.2 |
| SAVE5 | 371 | 5.7 |
</details>

## Q2 · AOV by state (≈7 min)

> "Which states have the highest average order value in 2025? Only include states with at least 100 valid orders."

**Looking for:** compute revenue **per order first** (a CTE), then average per state. Averaging line items gives the
average *line* value, not AOV. Then `HAVING COUNT(*) >= 100`.

- **Hint 1:** "What's the grain of order_items vs the grain you need for AOV?"
- **Hint 2:** "Where does a filter on an aggregate go: WHERE or HAVING?"
- **Follow-up:** "Delhi and Telangana differ by ₹1.57. Would you tell the business Delhi has higher AOV?" (No: that
  difference is noise. Report a confidence interval, or say they're effectively tied. The meaningful gap is Gujarat at
  ₹2,683, about 15% below the top.)

<details><summary>Answer key</summary>

```sql
WITH ov AS (
  SELECT o.order_id, c.state, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o
  JOIN customers c    ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
  GROUP BY o.order_id, c.state)
SELECT state, COUNT(*) AS orders, ROUND(AVG(revenue), 2) AS aov
FROM ov
GROUP BY state
HAVING COUNT(*) >= 100
ORDER BY aov DESC;
```

13 states qualify. Top 3: **Delhi ₹3,157.33** (936 orders), Telangana ₹3,155.76 (595), Uttar Pradesh ₹3,121.66 (558).
Bottom: Gujarat ₹2,683.46 (289).
</details>

## Q3 · 90-day value per sign-up (≈10 min)

> "For customers who signed up in the first half of 2025, what's the average revenue per sign-up in their first 90 days,
> by acquisition channel? People who never ordered count as zero."

**Looking for:** a date condition relative to *each customer's* sign-up date (`julianday(order_ts) < julianday(signup_date) + 90`),
a `LEFT JOIN` from the cohort, and `COALESCE(revenue, 0)` so non-buyers stay in the denominator.

- **Hint 1:** "The 90-day window is different for every customer. Where does that condition go?"
- **Hint 2:** "If you AVG only over customers who bought, what happens to channels with low conversion?"
- **Follow-up:** "Why use a fixed 90-day window rather than 'all revenue so far'?" (It makes cohorts comparable:
  January sign-ups have had longer to spend than June sign-ups. Fixed windows remove that bias.)

<details><summary>Answer key</summary>

```sql
WITH cohort AS (
  SELECT customer_id, acquisition_channel, signup_date
  FROM customers
  WHERE signup_date >= '2025-01-01' AND signup_date < '2025-07-01'),
rev90 AS (
  SELECT c.customer_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM cohort c
  JOIN orders o       ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
    AND julianday(o.order_ts) < julianday(c.signup_date) + 90
  GROUP BY c.customer_id)
SELECT c.acquisition_channel,
       COUNT(*) AS signups,
       ROUND(AVG(COALESCE(r.revenue, 0)), 2) AS revenue_per_signup_90d
FROM cohort c LEFT JOIN rev90 r ON r.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY revenue_per_signup_90d DESC;
```

| channel | sign-ups | 90-day revenue per sign-up (₹) |
|---|---:|---:|
| Referral | 281 | 4,140.30 |
| Email | 162 | 3,610.74 |
| Organic Search | 579 | 3,367.97 |
| Paid Search | 391 | 2,775.20 |
| Paid Social | 514 | 2,290.87 |
| Affiliate | 169 | 2,038.31 |
</details>

## Q4 · Basket size (≈8 min)

> "How many units do customers buy per order? Show the distribution of valid orders by units per order (1, 2, 3, 4 or
> more), with each bucket's share of orders and its AOV."

**Looking for:** aggregate to order level first, then bucket with `CASE`, then aggregate again. Summing
`quantity`, not counting lines.

- **Hint:** "Is 'units' the number of rows in order_items, or something else?"
- **Follow-up:** "44% of orders have a single unit. What would you test to grow basket size?" ("Frequently bought
  together" recommendations (SQL Q39 finds the pairs), free-shipping thresholds, and bundles. Measure the impact on
  units per order *and* margin.)

<details><summary>Answer key</summary>

```sql
WITH baskets AS (
  SELECT o.order_id,
         SUM(oi.quantity) AS units,
         SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
  GROUP BY o.order_id)
SELECT CASE WHEN units >= 4 THEN '4+' ELSE CAST(units AS TEXT) END AS basket_units,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders,
       ROUND(AVG(revenue), 2) AS aov
FROM baskets
GROUP BY basket_units
ORDER BY basket_units;
```

| units | orders | % | AOV (₹) |
|---|---:|---:|---:|
| 1 | 4,430 | 43.8 | 1,492.56 |
| 2 | 2,755 | 27.2 | 2,930.84 |
| 3 | 1,628 | 16.1 | 4,324.42 |
| 4+ | 1,312 | 13.0 | 6,711.36 |
</details>

## Q5 · Q1 churn (stretch, ≈8 min)

> "Of the customers who bought in Q1 2025, how many never bought again for the rest of the year, and how much Q1 revenue
> did those churned customers represent?"

**Looking for:** Q1 buyers in a CTE, then `NOT EXISTS` for any valid order from April to December, then conditional sums.

- **Hint:** "How do you express 'there is no later order' in SQL?"
- **Follow-up:** "59% churn sounds terrible. Is it?" (Compare with a benchmark first: the same metric for Q1 2024, or by
  channel. E-commerce purchase frequency is low, so many 'churned' customers are just infrequent buyers. A 9-month
  window is short for some categories.)

<details><summary>Answer key</summary>

**984 Q1 buyers; 583 (59%) didn't buy again in 2025; they spent ₹2,029,348.20 in Q1.**

```sql
WITH q1 AS (
  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS q1_revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status IN ('Delivered','Shipped')
    AND o.order_ts >= '2025-01-01' AND o.order_ts < '2025-04-01'
  GROUP BY o.customer_id)
SELECT COUNT(*) AS q1_buyers,
       SUM(NOT EXISTS (SELECT 1 FROM orders o
                       WHERE o.customer_id = q1.customer_id AND o.status IN ('Delivered','Shipped')
                         AND o.order_ts >= '2025-04-01' AND o.order_ts < '2026-01-01')) AS churned,
       ROUND(SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM orders o
                       WHERE o.customer_id = q1.customer_id AND o.status IN ('Delivered','Shipped')
                         AND o.order_ts >= '2025-04-01' AND o.order_ts < '2026-01-01')
                      THEN q1_revenue ELSE 0 END), 2) AS churned_q1_revenue
FROM q1;
```
</details>

## Q6 · Curveball: shipping fees (≈4 min)

> "Quick one: how much did we collect in shipping fees on valid 2025 orders?"

**Looking for:** the answer straight from `orders`. The trap is reusing the revenue query and joining `order_items`,
which repeats each order's shipping fee once per line (fan-out).

- **Hint:** "Which table does shipping_fee live in, and what's its grain?"
- **Follow-up:** "Someone else's dashboard says ₹32,046. What happened?" (They joined order_items, so orders with several
  lines had their fee counted several times. Fan-out inflates any order-level measure after a join to a child table.)

<details><summary>Answer key</summary>

**₹31,899.00.** The joined (wrong) version gives ₹32,046.00. Most orders ship free (90.7%), which is why the gap is small
here. With paid shipping on every order, it would be large.

```sql
SELECT ROUND(SUM(shipping_fee), 2) AS shipping_fees
FROM orders
WHERE status IN ('Delivered','Shipped')
  AND order_ts >= '2025-01-01' AND order_ts < '2026-01-01';
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
