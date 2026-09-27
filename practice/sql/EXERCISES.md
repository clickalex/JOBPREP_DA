# SQL Practice — 40 interview-style questions

Database: `data/shopkart.db` (see the [data dictionary](../../data/README.md)). Write each answer in `my_answers/qNN.sql`, then grade yourself with `python practice/sql/check.py`.

> **Conventions (apply to every question)**
> * **Net line revenue** = `quantity * unit_price - discount` (INR, from `order_items`)
> * A **valid order** has `status IN ('Delivered', 'Shipped')` — cancelled & returned orders earn nothing
> * Revenue **excludes shipping fees** unless stated
> * Round money to **2 dp** and percentages to **1 dp** (unless stated)
> * Dialect is **SQLite** — dates are ISO text, so use `strftime('%Y-%m', col)` and `julianday()`.
>   The [SQL guide](../../study-guide/01-sql.md#7-dialect-cheat-sheet) maps these to PostgreSQL / MySQL / SQL Server.


| # | Level | Topic | Title |
|---|---|---|---|
| [1](#q01) | Easy | SELECT, WHERE, ORDER BY | Premium electronics |
| [2](#q02) | Easy | COUNT, date filtering | 2025 sign-ups |
| [3](#q03) | Easy | GROUP BY | Orders by status |
| [4](#q04) | Easy | GROUP BY, LIMIT | Top 5 cities |
| [5](#q05) | Easy | GROUP BY, share of total | Payment mix |
| [6](#q06) | Easy | LIKE, string matching | Yahoo users |
| [7](#q07) | Easy | Aggregates | Price range per category |
| [8](#q08) | Easy | CASE WHEN, NULL handling | Coupon usage |
| [9](#q09) | Easy | JOIN, SUM | Total net revenue |
| [10](#q10) | Easy | Dates, strftime, GROUP BY | Monthly orders in 2025 |
| [11](#q11) | Easy | Timestamp ranges (classic trap) | October 2025 orders |
| [12](#q12) | Easy | WHERE, ORDER BY multiple keys | Well-paid analysts |
| [13](#q13) | Medium | Multi-table JOIN, GROUP BY | Revenue by category |
| [14](#q14) | Medium | LEFT JOIN / anti-join | Signed up, never ordered |
| [15](#q15) | Medium | JOIN, COUNT DISTINCT, string concat | Top 10 customers |
| [16](#q16) | Medium | CTE, two-level aggregation | AOV by device |
| [17](#q17) | Medium | Conditional aggregation, rates | Return rate by category |
| [18](#q18) | Medium | Conditional aggregation, AVG of boolean | Cancellations by payment method |
| [19](#q19) | Medium | JOIN, derived metrics | Gross margin by category |
| [20](#q20) | Medium | SELF JOIN | Who reports to whom |
| [21](#q21) | Medium | Subquery / DENSE_RANK (classic) | Second-highest salary |
| [22](#q22) | Medium | Window functions: RANK per group | Top earner per department |
| [23](#q23) | Medium | HAVING / INTERSECT | Customers active in both years |
| [24](#q24) | Medium | Top-N per group (ROW_NUMBER) | Best seller in each category |
| [25](#q25) | Medium | LAG, growth rates | Month-over-month growth |
| [26](#q26) | Medium | Running total (SUM OVER) | 2025 revenue, cumulative |
| [27](#q27) | Medium | ROW_NUMBER / LEAD, date arithmetic | Time to second order |
| [28](#q28) | Medium | Funnel analysis | Conversion funnel by device |
| [29](#q29) | Hard | CTE, first-order logic, conditional SUM | New vs returning revenue |
| [30](#q30) | Hard | Cohort retention | Monthly cohort retention |
| [31](#q31) | Hard | Moving average (window frame) | 3-month moving average |
| [32](#q32) | Hard | Cumulative share / Pareto | The 80/20 rule |
| [33](#q33) | Hard | Segmentation with CASE, recency/frequency | Rule-based customer segments |
| [34](#q34) | Hard | Anomaly hunting, HAVING | Find the operational incident |
| [35](#q35) | Hard | Experiment readout | A/B test summary |
| [36](#q36) | Hard | LAG within partitions | Longest gap between orders |
| [37](#q37) | Hard | Median without MEDIAN() | Median order value |
| [38](#q38) | Hard | Pivot with conditional aggregation, YoY | Diwali month, year over year |
| [39](#q39) | Hard | Self-join for pairs (market basket) | Frequently bought together |
| [40](#q40) | Hard | Business question end-to-end | Do welcome coupons create loyal customers? |

## Easy

### Q01
**Premium electronics** · _SELECT, WHERE, ORDER BY_

List every product in the **Electronics** category with a `list_price` above ₹2,000. Return `product_name`, `list_price`, most expensive first.

Expected columns: `product_name, list_price` · 5 row(s) · row order matters

### Q02
**2025 sign-ups** · _COUNT, date filtering_

How many customers signed up in calendar year 2025? Return a single column `signups_2025`.

Expected columns: `signups_2025` · 1 row(s) · any row order

### Q03
**Orders by status** · _GROUP BY_

Count orders by `status`. Return `status`, `n_orders`, most common first.

Expected columns: `status, n_orders` · 4 row(s) · row order matters

### Q04
**Top 5 cities** · _GROUP BY, LIMIT_

Which 5 cities have the most customers? Return `city`, `n_customers`, highest first.

Expected columns: `city, n_customers` · 5 row(s) · row order matters

### Q05
**Payment mix** · _GROUP BY, share of total_

For each `payment_method` return the number of orders and its share of all orders as a percentage rounded to 1 decimal. Columns: `payment_method`, `n_orders`, `pct_orders`; highest `n_orders` first.

Expected columns: `payment_method, n_orders, pct_orders` · 5 row(s) · row order matters

### Q06
**Yahoo users** · _LIKE, string matching_

How many customers have an email address at `yahoo.in`? Return `n_customers`.

Expected columns: `n_customers` · 1 row(s) · any row order

### Q07
**Price range per category** · _Aggregates_

For each product `category` return the average (2 dp), minimum and maximum `list_price`. Columns: `category`, `avg_price`, `min_price`, `max_price`; highest average first.

Expected columns: `category, avg_price, min_price, max_price` · 6 row(s) · row order matters

### Q08
**Coupon usage** · _CASE WHEN, NULL handling_

How many orders used a coupon and how many did not? Return `coupon_used` ('Yes' / 'No') and `n_orders`. *(Hint: missing coupons are stored as NULL — `= NULL` never matches.)*

Expected columns: `coupon_used, n_orders` · 2 row(s) · any row order

### Q09
**Total net revenue** · _JOIN, SUM_

What is ShopKart's total net revenue from valid orders (all time)? Return `total_net_revenue` rounded to 2 dp.

Expected columns: `total_net_revenue` · 1 row(s) · any row order

### Q10
**Monthly orders in 2025** · _Dates, strftime, GROUP BY_

Count all orders (any status) per month in 2025. Return `month` formatted `YYYY-MM` and `n_orders`, in calendar order.

Expected columns: `month, n_orders` · 12 row(s) · row order matters

### Q11
**October 2025 orders** · _Timestamp ranges (classic trap)_

How many orders were placed in October 2025? Return `n_orders`. *(Careful: `order_ts` contains a time. What does `BETWEEN '2025-10-01' AND '2025-10-31'` miss?)*

Expected columns: `n_orders` · 1 row(s) · any row order

### Q12
**Well-paid analysts** · _WHERE, ORDER BY multiple keys_

List employees in the **Analytics** department earning at least ₹1,00,000 per month. Return `full_name`, `monthly_salary`; highest salary first, then name A→Z.

Expected columns: `full_name, monthly_salary` · 3 row(s) · row order matters


## Medium

### Q13
**Revenue by category** · _Multi-table JOIN, GROUP BY_

Net revenue from valid orders by product `category`. Return `category`, `net_revenue` (2 dp), highest first.

Expected columns: `category, net_revenue` · 6 row(s) · row order matters

### Q14
**Signed up, never ordered** · _LEFT JOIN / anti-join_

How many customers have **never placed an order** (of any status)? Return `n_customers`.

Expected columns: `n_customers` · 1 row(s) · any row order

### Q15
**Top 10 customers** · _JOIN, COUNT DISTINCT, string concat_

Top 10 customers by lifetime net revenue (valid orders). Return `customer_id`, `customer_name` (first + ' ' + last), `n_orders`, `net_revenue` (2 dp); highest revenue first. *(Watch out: joining to order_items multiplies rows — count orders with DISTINCT.)*

Expected columns: `customer_id, customer_name, n_orders, net_revenue` · 10 row(s) · row order matters

### Q16
**AOV by device** · _CTE, two-level aggregation_

Average order value (AOV = mean net item revenue per valid order, excluding shipping) by `device`. Return `device`, `n_orders`, `aov` (2 dp); highest AOV first.

Expected columns: `device, n_orders, aov` · 3 row(s) · row order matters

### Q17
**Return rate by category** · _Conditional aggregation, rates_

For order lines whose order was either **Delivered** or **Returned**, what percentage belonged to a Returned order, by `category`? Return `category`, `n_lines`, `return_rate_pct` (1 dp); highest rate first.

Expected columns: `category, n_lines, return_rate_pct` · 6 row(s) · row order matters

### Q18
**Cancellations by payment method** · _Conditional aggregation, AVG of boolean_

Cancellation rate (share of orders with status 'Cancelled') by `payment_method`. Return `payment_method`, `n_orders`, `cancel_rate_pct` (1 dp); highest rate first.

Expected columns: `payment_method, n_orders, cancel_rate_pct` · 5 row(s) · row order matters

### Q19
**Gross margin by category** · _JOIN, derived metrics_

For valid orders compute by `category`: `net_revenue`, `cogs` (quantity × unit_cost) and `gross_margin_pct` = (net_revenue − cogs) / net_revenue × 100. Money 2 dp, pct 1 dp. Highest margin % first.

Expected columns: `category, net_revenue, cogs, gross_margin_pct` · 6 row(s) · row order matters

### Q20
**Who reports to whom** · _SELF JOIN_

List every employee with their manager's name. Return `employee`, `manager` (NULL for the CEO), ordered by `employee_id`.

Expected columns: `employee, manager` · 30 row(s) · row order matters

### Q21
**Second-highest salary** · _Subquery / DENSE_RANK (classic)_

What is the second-highest **distinct** monthly salary in the company? Return `second_highest_salary`.

Expected columns: `second_highest_salary` · 1 row(s) · any row order

### Q22
**Top earner per department** · _Window functions: RANK per group_

Highest-paid employee(s) in each department (keep ties). Return `department`, `full_name`, `monthly_salary`, ordered by department then name.

Expected columns: `department, full_name, monthly_salary` · 6 row(s) · row order matters

### Q23
**Customers active in both years** · _HAVING / INTERSECT_

How many customers placed at least one order (any status) in **both** 2024 and 2025? Return `n_customers`.

Expected columns: `n_customers` · 1 row(s) · any row order

### Q24
**Best seller in each category** · _Top-N per group (ROW_NUMBER)_

For each `category`, the product with the most units sold in valid orders. Return `category`, `product_name`, `units_sold`, ordered by category.

Expected columns: `category, product_name, units_sold` · 6 row(s) · row order matters

### Q25
**Month-over-month growth** · _LAG, growth rates_

Monthly net revenue (valid orders) with the previous month's value and MoM growth %. Return `month`, `net_revenue`, `prev_month_revenue`, `mom_growth_pct` (1 dp; NULL for the first month), in calendar order.

Expected columns: `month, net_revenue, prev_month_revenue, mom_growth_pct` · 24 row(s) · row order matters

### Q26
**2025 revenue, cumulative** · _Running total (SUM OVER)_

For each month of 2025 return `month`, `net_revenue` and `running_total` (year-to-date), both 2 dp.

Expected columns: `month, net_revenue, running_total` · 12 row(s) · row order matters

### Q27
**Time to second order** · _ROW_NUMBER / LEAD, date arithmetic_

Among customers with at least 2 orders (any status), what is the average number of days between their first and second order? Return `avg_days_to_second_order` (1 dp). *(SQLite: `julianday(b) - julianday(a)` gives days.)*

Expected columns: `avg_days_to_second_order` · 1 row(s) · any row order

### Q28
**Conversion funnel by device** · _Funnel analysis_

Using `web_sessions`, for each `device` return `sessions` and the % of sessions reaching each step (1 dp): `product_view_pct`, `add_to_cart_pct`, `checkout_pct`, `purchase_pct`. Highest purchase % first.

Expected columns: `device, sessions, product_view_pct, add_to_cart_pct, checkout_pct, purchase_pct` · 3 row(s) · row order matters


## Hard

### Q29
**New vs returning revenue** · _CTE, first-order logic, conditional SUM_

For each month of 2025, split net revenue (valid orders) into revenue from orders that were the customer's **first-ever order** (of any status) vs all later orders. Return `month`, `new_customer_revenue`, `returning_customer_revenue` (2 dp), calendar order.

Expected columns: `month, new_customer_revenue, returning_customer_revenue` · 12 row(s) · row order matters

### Q30
**Monthly cohort retention** · _Cohort retention_

Group customers into cohorts by the month of their first order (any status). For the cohorts **2025-01 to 2025-06**, return `cohort_month`, `cohort_size` and the % of the cohort that placed any order exactly 1, 2 and 3 months later: `m1_pct`, `m2_pct`, `m3_pct` (1 dp).

Expected columns: `cohort_month, cohort_size, m1_pct, m2_pct, m3_pct` · 6 row(s) · row order matters

### Q31
**3-month moving average** · _Moving average (window frame)_

Monthly net revenue (valid orders) for all months with a trailing 3-month moving average (current + 2 previous months; early months average what's available). Return `month`, `net_revenue`, `ma_3m` (2 dp).

Expected columns: `month, net_revenue, ma_3m` · 24 row(s) · row order matters

### Q32
**The 80/20 rule** · _Cumulative share / Pareto_

Rank buying customers by lifetime net revenue (valid orders). What is the smallest number of top customers that together generate at least 80% of revenue, and what % of all buying customers is that? Return `n_customers_for_80pct`, `pct_of_buyers` (1 dp).

Expected columns: `n_customers_for_80pct, pct_of_buyers` · 1 row(s) · any row order

### Q33
**Rule-based customer segments** · _Segmentation with CASE, recency/frequency_

As of **2026-01-01**, segment every customer with at least one valid order. Let `orders` = # valid orders and `recency` = days since their last valid order. Apply rules in this order:
  1. `Champion`: orders ≥ 4 and recency ≤ 90
  2. `Loyal`: orders ≥ 2 and recency ≤ 180
  3. `At Risk`: orders ≥ 2 (and recency > 180)
  4. `New`: orders = 1 and recency ≤ 90
  5. `Lapsed One-timer`: everyone else

Return `segment`, `n_customers`, `avg_revenue` (2 dp), largest segment first.

Expected columns: `segment, n_customers, avg_revenue` · 5 row(s) · row order matters

### Q34
**Find the operational incident** · _Anomaly hunting, HAVING_

Something went wrong somewhere in 2025. Find the **state + month** combination with the highest cancellation rate among those with at least 30 orders. Return `state`, `month`, `n_orders`, `cancel_rate_pct` (1 dp) — just the top row.

Expected columns: `state, month, n_orders, cancel_rate_pct` · 1 row(s) · row order matters

### Q35
**A/B test summary** · _Experiment readout_

Summarise `checkout_experiment` by `variant` and `device`: `visitors`, `conversions`, `conv_rate_pct` (2 dp), `revenue_per_visitor` (2 dp). Order by device, then variant. *(Then think: is the lift the same everywhere? See the statistics guide for the significance test.)*

Expected columns: `variant, device, visitors, conversions, conv_rate_pct, revenue_per_visitor` · 6 row(s) · row order matters

### Q36
**Longest gap between orders** · _LAG within partitions_

Across all customers, what is the longest gap (in whole days, using `julianday` difference rounded down) between two consecutive orders by the same customer? Return `max_gap_days`.

Expected columns: `max_gap_days` · 1 row(s) · any row order

### Q37
**Median order value** · _Median without MEDIAN()_

What is the **median** net order value of valid orders (item revenue, excluding shipping)? SQLite has no MEDIAN function. Return `median_order_value` (2 dp).

Expected columns: `median_order_value` · 1 row(s) · any row order

### Q38
**Diwali month, year over year** · _Pivot with conditional aggregation, YoY_

Compare October 2024 vs October 2025 net revenue (valid orders) by `category`. Return `category`, `rev_oct_2024`, `rev_oct_2025` (2 dp) and `yoy_growth_pct` (1 dp); highest growth first.

Expected columns: `category, rev_oct_2024, rev_oct_2025, yoy_growth_pct` · 6 row(s) · row order matters

### Q39
**Frequently bought together** · _Self-join for pairs (market basket)_

Which pairs of products appear together in the same order most often (any status)? Count each pair once (lower product_id first). Return `product_a`, `product_b` (names) and `n_orders` for the top 5, ties broken by product_a then product_b name.

Expected columns: `product_a, product_b, n_orders` · 5 row(s) · row order matters

### Q40
**Do welcome coupons create loyal customers?** · _Business question end-to-end_

For customers whose first order (any status) was placed before **2025-07-01**, compare those whose first order used `WELCOME15` with those whose first order used no coupon. Return `first_order_type` ('WELCOME15' / 'No coupon'), `n_customers` and `repeat_180d_pct` = % who placed another order within 180 days of the first (1 dp). Ignore other coupon codes.

Expected columns: `first_order_type, n_customers, repeat_180d_pct` · 2 row(s) · any row order

