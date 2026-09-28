"""
Single source of truth for the SQL practice set.

Each question has: id, level, topics, title, prompt, expected columns, the
reference solution, and whether row ORDER matters when checking.
`build.py` turns this into EXERCISES.md / SOLUTIONS.md / starter files and
`check.py` grades your answers against the reference solutions.

Conventions used in every question (also written at the top of EXERCISES.md):
  * net line revenue  = quantity * unit_price - discount           (INR)
  * a "valid" order   = status IN ('Delivered', 'Shipped')
  * revenue excludes shipping fees unless the question says otherwise
  * round money to 2 decimals, percentages to 1 decimal
"""

QUESTIONS = [
    # ------------------------------------------------------------------ EASY
    dict(
        id=1, level="Easy", topics="SELECT, WHERE, ORDER BY",
        title="Premium electronics",
        prompt="List every product in the **Electronics** category with a `list_price` above ₹2,000. "
               "Return `product_name`, `list_price`, most expensive first.",
        ordered=True,
        solution="""
SELECT product_name, list_price
FROM products
WHERE category = 'Electronics'
  AND list_price > 2000
ORDER BY list_price DESC;
"""),
    dict(
        id=2, level="Easy", topics="COUNT, date filtering",
        title="2025 sign-ups",
        prompt="How many customers signed up in calendar year 2025? Return a single column `signups_2025`.",
        ordered=False,
        solution="""
SELECT COUNT(*) AS signups_2025
FROM customers
WHERE signup_date >= '2025-01-01'
  AND signup_date <  '2026-01-01';
"""),
    dict(
        id=3, level="Easy", topics="GROUP BY",
        title="Orders by status",
        prompt="Count orders by `status`. Return `status`, `n_orders`, most common first.",
        ordered=True,
        solution="""
SELECT status, COUNT(*) AS n_orders
FROM orders
GROUP BY status
ORDER BY n_orders DESC;
"""),
    dict(
        id=4, level="Easy", topics="GROUP BY, LIMIT",
        title="Top 5 cities",
        prompt="Which 5 cities have the most customers? Return `city`, `n_customers`, highest first.",
        ordered=True,
        solution="""
SELECT city, COUNT(*) AS n_customers
FROM customers
GROUP BY city
ORDER BY n_customers DESC
LIMIT 5;
"""),
    dict(
        id=5, level="Easy", topics="GROUP BY, share of total",
        title="Payment mix",
        prompt="For each `payment_method` return the number of orders and its share of all orders as a "
               "percentage rounded to 1 decimal. Columns: `payment_method`, `n_orders`, `pct_orders`; "
               "highest `n_orders` first.",
        ordered=True,
        solution="""
SELECT payment_method,
       COUNT(*) AS n_orders,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS pct_orders
FROM orders
GROUP BY payment_method
ORDER BY n_orders DESC;
"""),
    dict(
        id=6, level="Easy", topics="LIKE, string matching",
        title="Yahoo users",
        prompt="How many customers have an email address at `yahoo.in`? Return `n_customers`.",
        ordered=False,
        solution="""
SELECT COUNT(*) AS n_customers
FROM customers
WHERE email LIKE '%@yahoo.in';
"""),
    dict(
        id=7, level="Easy", topics="Aggregates",
        title="Price range per category",
        prompt="For each product `category` return the average (2 dp), minimum and maximum `list_price`. "
               "Columns: `category`, `avg_price`, `min_price`, `max_price`; highest average first.",
        ordered=True,
        solution="""
SELECT category,
       ROUND(AVG(list_price), 2) AS avg_price,
       MIN(list_price)           AS min_price,
       MAX(list_price)           AS max_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;
"""),
    dict(
        id=8, level="Easy", topics="CASE WHEN, NULL handling",
        title="Coupon usage",
        prompt="How many orders used a coupon and how many did not? Return `coupon_used` ('Yes' / 'No') "
               "and `n_orders`. *(Hint: missing coupons are stored as NULL — `= NULL` never matches.)*",
        ordered=False,
        solution="""
SELECT CASE WHEN coupon_code IS NULL THEN 'No' ELSE 'Yes' END AS coupon_used,
       COUNT(*) AS n_orders
FROM orders
GROUP BY coupon_used;
"""),
    dict(
        id=9, level="Easy", topics="JOIN, SUM",
        title="Total net revenue",
        prompt="What is ShopKart's total net revenue from valid orders (all time)? Return `total_net_revenue` "
               "rounded to 2 dp.",
        ordered=False,
        solution="""
SELECT ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS total_net_revenue
FROM order_items AS oi
JOIN orders      AS o ON o.order_id = oi.order_id
WHERE o.status IN ('Delivered', 'Shipped');
"""),
    dict(
        id=10, level="Easy", topics="Dates, strftime, GROUP BY",
        title="Monthly orders in 2025",
        prompt="Count all orders (any status) per month in 2025. Return `month` formatted `YYYY-MM` and "
               "`n_orders`, in calendar order.",
        ordered=True,
        solution="""
SELECT strftime('%Y-%m', order_ts) AS month,
       COUNT(*) AS n_orders
FROM orders
WHERE order_ts >= '2025-01-01' AND order_ts < '2026-01-01'
GROUP BY month
ORDER BY month;
"""),
    dict(
        id=11, level="Easy", topics="Timestamp ranges (classic trap)",
        title="October 2025 orders",
        prompt="How many orders were placed in October 2025? Return `n_orders`. "
               "*(Careful: `order_ts` contains a time. What does `BETWEEN '2025-10-01' AND '2025-10-31'` miss?)*",
        ordered=False,
        solution="""
-- BETWEEN '2025-10-01' AND '2025-10-31' would silently drop everything
-- placed on 31 Oct after midnight. Use a half-open range instead.
SELECT COUNT(*) AS n_orders
FROM orders
WHERE order_ts >= '2025-10-01'
  AND order_ts <  '2025-11-01';
"""),
    dict(
        id=12, level="Easy", topics="WHERE, ORDER BY multiple keys",
        title="Well-paid analysts",
        prompt="List employees in the **Analytics** department earning at least ₹1,00,000 per month. "
               "Return `full_name`, `monthly_salary`; highest salary first, then name A→Z.",
        ordered=True,
        solution="""
SELECT full_name, monthly_salary
FROM employees
WHERE department = 'Analytics'
  AND monthly_salary >= 100000
ORDER BY monthly_salary DESC, full_name;
"""),

    # ---------------------------------------------------------------- MEDIUM
    dict(
        id=13, level="Medium", topics="Multi-table JOIN, GROUP BY",
        title="Revenue by category",
        prompt="Net revenue from valid orders by product `category`. Return `category`, `net_revenue` (2 dp), "
               "highest first.",
        ordered=True,
        solution="""
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS net_revenue
FROM order_items AS oi
JOIN orders      AS o ON o.order_id  = oi.order_id
JOIN products    AS p ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY net_revenue DESC;
"""),
    dict(
        id=14, level="Medium", topics="LEFT JOIN / anti-join",
        title="Signed up, never ordered",
        prompt="How many customers have **never placed an order** (of any status)? Return `n_customers`.",
        ordered=False,
        solution="""
SELECT COUNT(*) AS n_customers
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- Equivalent: WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
"""),
    dict(
        id=15, level="Medium", topics="JOIN, COUNT DISTINCT, string concat",
        title="Top 10 customers",
        prompt="Top 10 customers by lifetime net revenue (valid orders). Return `customer_id`, `customer_name` "
               "(first + ' ' + last), `n_orders`, `net_revenue` (2 dp); highest revenue first. "
               "*(Watch out: joining to order_items multiplies rows — count orders with DISTINCT.)*",
        ordered=True,
        solution="""
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name                        AS customer_name,
       COUNT(DISTINCT o.order_id)                                AS n_orders,
       ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2)  AS net_revenue
FROM customers   AS c
JOIN orders      AS o  ON o.customer_id = c.customer_id
JOIN order_items AS oi ON oi.order_id   = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, customer_name
ORDER BY net_revenue DESC
LIMIT 10;
"""),
    dict(
        id=16, level="Medium", topics="CTE, two-level aggregation",
        title="AOV by device",
        prompt="Average order value (AOV = mean net item revenue per valid order, excluding shipping) by `device`. "
               "Return `device`, `n_orders`, `aov` (2 dp); highest AOV first.",
        ordered=True,
        solution="""
WITH order_value AS (
    SELECT o.order_id, o.device,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS order_revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY o.order_id, o.device
)
SELECT device,
       COUNT(*)                      AS n_orders,
       ROUND(AVG(order_revenue), 2)  AS aov
FROM order_value
GROUP BY device
ORDER BY aov DESC;
"""),
    dict(
        id=17, level="Medium", topics="Conditional aggregation, rates",
        title="Return rate by category",
        prompt="For order lines whose order was either **Delivered** or **Returned**, what percentage belonged to a "
               "Returned order, by `category`? Return `category`, `n_lines`, `return_rate_pct` (1 dp); highest rate first.",
        ordered=True,
        solution="""
SELECT p.category,
       COUNT(*) AS n_lines,
       ROUND(100.0 * SUM(CASE WHEN o.status = 'Returned' THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM order_items AS oi
JOIN orders   AS o ON o.order_id   = oi.order_id
JOIN products AS p ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Returned')
GROUP BY p.category
ORDER BY return_rate_pct DESC;
"""),
    dict(
        id=18, level="Medium", topics="Conditional aggregation, AVG of boolean",
        title="Cancellations by payment method",
        prompt="Cancellation rate (share of orders with status 'Cancelled') by `payment_method`. "
               "Return `payment_method`, `n_orders`, `cancel_rate_pct` (1 dp); highest rate first.",
        ordered=True,
        solution="""
SELECT payment_method,
       COUNT(*) AS n_orders,
       ROUND(100.0 * AVG(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END), 1) AS cancel_rate_pct
FROM orders
GROUP BY payment_method
ORDER BY cancel_rate_pct DESC;
"""),
    dict(
        id=19, level="Medium", topics="JOIN, derived metrics",
        title="Gross margin by category",
        prompt="For valid orders compute by `category`: `net_revenue`, `cogs` (quantity × unit_cost) and "
               "`gross_margin_pct` = (net_revenue − cogs) / net_revenue × 100. Money 2 dp, pct 1 dp. "
               "Highest margin % first.",
        ordered=True,
        solution="""
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS net_revenue,
       ROUND(SUM(oi.quantity * p.unit_cost), 2)                AS cogs,
       ROUND(100.0 * (SUM(oi.quantity * oi.unit_price - oi.discount) - SUM(oi.quantity * p.unit_cost))
                   / SUM(oi.quantity * oi.unit_price - oi.discount), 1) AS gross_margin_pct
FROM order_items AS oi
JOIN orders   AS o ON o.order_id   = oi.order_id
JOIN products AS p ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY gross_margin_pct DESC;
"""),
    dict(
        id=20, level="Medium", topics="SELF JOIN",
        title="Who reports to whom",
        prompt="List every employee with their manager's name. Return `employee`, `manager` (NULL for the CEO), "
               "ordered by `employee_id`.",
        ordered=True,
        solution="""
SELECT e.full_name AS employee,
       m.full_name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.employee_id = e.manager_id
ORDER BY e.employee_id;
"""),
    dict(
        id=21, level="Medium", topics="Subquery / DENSE_RANK (classic)",
        title="Second-highest salary",
        prompt="What is the second-highest **distinct** monthly salary in the company? Return `second_highest_salary`.",
        ordered=False,
        solution="""
SELECT MAX(monthly_salary) AS second_highest_salary
FROM employees
WHERE monthly_salary < (SELECT MAX(monthly_salary) FROM employees);

-- Window-function version (generalises to Nth highest):
-- SELECT DISTINCT monthly_salary FROM (
--   SELECT monthly_salary, DENSE_RANK() OVER (ORDER BY monthly_salary DESC) AS rnk FROM employees
-- ) WHERE rnk = 2;
"""),
    dict(
        id=22, level="Medium", topics="Window functions: RANK per group",
        title="Top earner per department",
        prompt="Highest-paid employee(s) in each department (keep ties). Return `department`, `full_name`, "
               "`monthly_salary`, ordered by department then name.",
        ordered=True,
        solution="""
WITH ranked AS (
    SELECT department, full_name, monthly_salary,
           RANK() OVER (PARTITION BY department ORDER BY monthly_salary DESC) AS rnk
    FROM employees
)
SELECT department, full_name, monthly_salary
FROM ranked
WHERE rnk = 1
ORDER BY department, full_name;
"""),
    dict(
        id=23, level="Medium", topics="HAVING / INTERSECT",
        title="Customers active in both years",
        prompt="How many customers placed at least one order (any status) in **both** 2024 and 2025? Return `n_customers`.",
        ordered=False,
        solution="""
SELECT COUNT(*) AS n_customers
FROM (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING SUM(CASE WHEN order_ts < '2025-01-01' THEN 1 ELSE 0 END) > 0
       AND SUM(CASE WHEN order_ts >= '2025-01-01' THEN 1 ELSE 0 END) > 0
);

-- Or: SELECT customer_id FROM orders WHERE order_ts < '2025-01-01'
--     INTERSECT
--     SELECT customer_id FROM orders WHERE order_ts >= '2025-01-01';
"""),
    dict(
        id=24, level="Medium", topics="Top-N per group (ROW_NUMBER)",
        title="Best seller in each category",
        prompt="For each `category`, the product with the most units sold in valid orders. Return `category`, "
               "`product_name`, `units_sold`, ordered by category.",
        ordered=True,
        solution="""
WITH units AS (
    SELECT p.category, p.product_name, SUM(oi.quantity) AS units_sold
    FROM order_items AS oi
    JOIN orders   AS o ON o.order_id   = oi.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY p.category, p.product_name
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY units_sold DESC, product_name) AS rn
    FROM units
)
SELECT category, product_name, units_sold
FROM ranked
WHERE rn = 1
ORDER BY category;
"""),
    dict(
        id=25, level="Medium", topics="LAG, growth rates",
        title="Month-over-month growth",
        prompt="Monthly net revenue (valid orders) with the previous month's value and MoM growth %. Return "
               "`month`, `net_revenue`, `prev_month_revenue`, `mom_growth_pct` (1 dp; NULL for the first month), "
               "in calendar order.",
        ordered=True,
        solution="""
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_ts) AS month,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS net_revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY month
)
SELECT month,
       ROUND(net_revenue, 2) AS net_revenue,
       ROUND(LAG(net_revenue) OVER (ORDER BY month), 2) AS prev_month_revenue,
       ROUND(100.0 * (net_revenue - LAG(net_revenue) OVER (ORDER BY month))
                   / LAG(net_revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;
"""),
    dict(
        id=26, level="Medium", topics="Running total (SUM OVER)",
        title="2025 revenue, cumulative",
        prompt="For each month of 2025 return `month`, `net_revenue` and `running_total` (year-to-date), both 2 dp.",
        ordered=True,
        solution="""
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_ts) AS month,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS net_revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
      AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
    GROUP BY month
)
SELECT month,
       ROUND(net_revenue, 2) AS net_revenue,
       ROUND(SUM(net_revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2)
           AS running_total
FROM monthly
ORDER BY month;
"""),
    dict(
        id=27, level="Medium", topics="ROW_NUMBER / LEAD, date arithmetic",
        title="Time to second order",
        prompt="Among customers with at least 2 orders (any status), what is the average number of days between their "
               "first and second order? Return `avg_days_to_second_order` (1 dp). "
               "*(SQLite: `julianday(b) - julianday(a)` gives days.)*",
        ordered=False,
        solution="""
WITH seq AS (
    SELECT customer_id, order_ts,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts, order_id) AS n
    FROM orders
)
SELECT ROUND(AVG(julianday(s2.order_ts) - julianday(s1.order_ts)), 1) AS avg_days_to_second_order
FROM seq AS s1
JOIN seq AS s2 ON s2.customer_id = s1.customer_id AND s2.n = 2
WHERE s1.n = 1;
"""),
    dict(
        id=28, level="Medium", topics="Funnel analysis",
        title="Conversion funnel by device",
        prompt="Using `web_sessions`, for each `device` return `sessions` and the % of sessions reaching each step "
               "(1 dp): `product_view_pct`, `add_to_cart_pct`, `checkout_pct`, `purchase_pct`. Highest purchase % first.",
        ordered=True,
        solution="""
SELECT device,
       COUNT(*) AS sessions,
       ROUND(100.0 * AVG(viewed_product), 1) AS product_view_pct,
       ROUND(100.0 * AVG(added_to_cart), 1)  AS add_to_cart_pct,
       ROUND(100.0 * AVG(began_checkout), 1) AS checkout_pct,
       ROUND(100.0 * AVG(purchased), 1)      AS purchase_pct
FROM web_sessions
GROUP BY device
ORDER BY purchase_pct DESC;
"""),

    # ------------------------------------------------------------------ HARD
    dict(
        id=29, level="Hard", topics="CTE, first-order logic, conditional SUM",
        title="New vs returning revenue",
        prompt="For each month of 2025, split net revenue (valid orders) into revenue from orders that were the "
               "customer's **first-ever order** (of any status) vs all later orders. Return `month`, "
               "`new_customer_revenue`, `returning_customer_revenue` (2 dp), calendar order.",
        ordered=True,
        solution="""
WITH first_order AS (
    SELECT customer_id, MIN(order_ts) AS first_ts
    FROM orders
    GROUP BY customer_id
), rev AS (
    SELECT o.order_id, o.order_ts,
           CASE WHEN o.order_ts = f.first_ts THEN 'new' ELSE 'returning' END AS kind,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
    FROM orders AS o
    JOIN first_order AS f  ON f.customer_id = o.customer_id
    JOIN order_items AS oi ON oi.order_id   = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
      AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
    GROUP BY o.order_id, o.order_ts, kind
)
SELECT strftime('%Y-%m', order_ts) AS month,
       ROUND(SUM(CASE WHEN kind = 'new' THEN revenue ELSE 0 END), 2)       AS new_customer_revenue,
       ROUND(SUM(CASE WHEN kind = 'returning' THEN revenue ELSE 0 END), 2) AS returning_customer_revenue
FROM rev
GROUP BY month
ORDER BY month;
"""),
    dict(
        id=30, level="Hard", topics="Cohort retention",
        title="Monthly cohort retention",
        prompt="Group customers into cohorts by the month of their first order (any status). For the cohorts "
               "**2025-01 to 2025-06**, return `cohort_month`, `cohort_size` and the % of the cohort that placed any "
               "order exactly 1, 2 and 3 months later: `m1_pct`, `m2_pct`, `m3_pct` (1 dp).",
        ordered=True,
        solution="""
WITH firsts AS (
    SELECT customer_id,
           MIN(order_ts) AS first_ts
    FROM orders
    GROUP BY customer_id
), activity AS (
    SELECT DISTINCT
           o.customer_id,
           strftime('%Y-%m', f.first_ts) AS cohort_month,
           (CAST(strftime('%Y', o.order_ts) AS INT) * 12 + CAST(strftime('%m', o.order_ts) AS INT))
         - (CAST(strftime('%Y', f.first_ts) AS INT) * 12 + CAST(strftime('%m', f.first_ts) AS INT)) AS month_n
    FROM orders AS o
    JOIN firsts AS f ON f.customer_id = o.customer_id
)
SELECT cohort_month,
       COUNT(DISTINCT CASE WHEN month_n = 0 THEN customer_id END) AS cohort_size,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 1 THEN customer_id END)
                   / COUNT(DISTINCT CASE WHEN month_n = 0 THEN customer_id END), 1) AS m1_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 2 THEN customer_id END)
                   / COUNT(DISTINCT CASE WHEN month_n = 0 THEN customer_id END), 1) AS m2_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 3 THEN customer_id END)
                   / COUNT(DISTINCT CASE WHEN month_n = 0 THEN customer_id END), 1) AS m3_pct
FROM activity
WHERE cohort_month BETWEEN '2025-01' AND '2025-06'
GROUP BY cohort_month
ORDER BY cohort_month;
"""),
    dict(
        id=31, level="Hard", topics="Moving average (window frame)",
        title="3-month moving average",
        prompt="Monthly net revenue (valid orders) for all months with a trailing 3-month moving average "
               "(current + 2 previous months; early months average what's available). Return `month`, "
               "`net_revenue`, `ma_3m` (2 dp).",
        ordered=True,
        solution="""
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_ts) AS month,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS net_revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY month
)
SELECT month,
       ROUND(net_revenue, 2) AS net_revenue,
       ROUND(AVG(net_revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma_3m
FROM monthly
ORDER BY month;
"""),
    dict(
        id=32, level="Hard", topics="Cumulative share / Pareto",
        title="The 80/20 rule",
        prompt="Rank buying customers by lifetime net revenue (valid orders). What is the smallest number of top "
               "customers that together generate at least 80% of revenue, and what % of all buying customers is that? "
               "Return `n_customers_for_80pct`, `pct_of_buyers` (1 dp).",
        ordered=False,
        solution="""
WITH cust AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY o.customer_id
), cum AS (
    SELECT customer_id,
           ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_id) AS rn,
           SUM(revenue) OVER (ORDER BY revenue DESC, customer_id
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
             / SUM(revenue) OVER () AS cum_share
    FROM cust
)
SELECT MIN(rn) AS n_customers_for_80pct,
       ROUND(100.0 * MIN(rn) / (SELECT COUNT(*) FROM cust), 1) AS pct_of_buyers
FROM cum
WHERE cum_share >= 0.8;
"""),
    dict(
        id=33, level="Hard", topics="Segmentation with CASE, recency/frequency",
        title="Rule-based customer segments",
        prompt="As of **2026-01-01**, segment every customer with at least one valid order. Let `orders` = # valid "
               "orders and `recency` = days since their last valid order. Apply rules in this order:\n"
               "  1. `Champion`: orders ≥ 4 and recency ≤ 90\n"
               "  2. `Loyal`: orders ≥ 2 and recency ≤ 180\n"
               "  3. `At Risk`: orders ≥ 2 (and recency > 180)\n"
               "  4. `New`: orders = 1 and recency ≤ 90\n"
               "  5. `Lapsed One-timer`: everyone else\n\n"
               "Return `segment`, `n_customers`, `avg_revenue` (2 dp), largest segment first.",
        ordered=True,
        solution="""
WITH per_order AS (
    SELECT o.customer_id, o.order_id, o.order_ts,
           SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY o.customer_id, o.order_id, o.order_ts
), rf AS (
    SELECT customer_id,
           COUNT(*)                                          AS n_orders,
           julianday('2026-01-01') - julianday(MAX(order_ts)) AS recency,
           SUM(revenue)                                      AS revenue
    FROM per_order
    GROUP BY customer_id
), seg AS (
    SELECT *,
           CASE WHEN n_orders >= 4 AND recency <= 90  THEN 'Champion'
                WHEN n_orders >= 2 AND recency <= 180 THEN 'Loyal'
                WHEN n_orders >= 2                    THEN 'At Risk'
                WHEN n_orders = 1  AND recency <= 90  THEN 'New'
                ELSE 'Lapsed One-timer' END AS segment
    FROM rf
)
SELECT segment, COUNT(*) AS n_customers, ROUND(AVG(revenue), 2) AS avg_revenue
FROM seg
GROUP BY segment
ORDER BY n_customers DESC;
"""),
    dict(
        id=34, level="Hard", topics="Anomaly hunting, HAVING",
        title="Find the operational incident",
        prompt="Something went wrong somewhere in 2025. Find the **state + month** combination with the highest "
               "cancellation rate among those with at least 30 orders. Return `state`, `month`, `n_orders`, "
               "`cancel_rate_pct` (1 dp) — just the top row.",
        ordered=True,
        solution="""
SELECT c.state,
       strftime('%Y-%m', o.order_ts) AS month,
       COUNT(*) AS n_orders,
       ROUND(100.0 * AVG(CASE WHEN o.status = 'Cancelled' THEN 1.0 ELSE 0 END), 1) AS cancel_rate_pct
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
GROUP BY c.state, month
HAVING COUNT(*) >= 30
ORDER BY cancel_rate_pct DESC
LIMIT 1;
"""),
    dict(
        id=35, level="Hard", topics="Experiment readout",
        title="A/B test summary",
        prompt="Summarise `checkout_experiment` by `variant` and `device`: `visitors`, `conversions`, "
               "`conv_rate_pct` (2 dp), `revenue_per_visitor` (2 dp). Order by device, then variant. "
               "*(Then think: is the lift the same everywhere? See the statistics guide for the significance test.)*",
        ordered=True,
        solution="""
SELECT variant, device,
       COUNT(*)                              AS visitors,
       SUM(converted)                        AS conversions,
       ROUND(100.0 * AVG(converted), 2)      AS conv_rate_pct,
       ROUND(AVG(order_value), 2)            AS revenue_per_visitor
FROM checkout_experiment
GROUP BY variant, device
ORDER BY device, variant;
"""),
    dict(
        id=36, level="Hard", topics="LAG within partitions",
        title="Longest gap between orders",
        prompt="Across all customers, what is the longest gap (in whole days, using `julianday` difference rounded "
               "down) between two consecutive orders by the same customer? Return `max_gap_days`.",
        ordered=False,
        solution="""
WITH gaps AS (
    SELECT customer_id,
           julianday(order_ts)
             - julianday(LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts, order_id)) AS gap
    FROM orders
)
SELECT CAST(MAX(gap) AS INTEGER) AS max_gap_days
FROM gaps;
"""),
    dict(
        id=37, level="Hard", topics="Median without MEDIAN()",
        title="Median order value",
        prompt="What is the **median** net order value of valid orders (item revenue, excluding shipping)? SQLite "
               "has no MEDIAN function. Return `median_order_value` (2 dp).",
        ordered=False,
        solution="""
WITH ov AS (
    SELECT o.order_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS v
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY o.order_id
), ranked AS (
    SELECT v,
           ROW_NUMBER() OVER (ORDER BY v) AS rn,
           COUNT(*) OVER ()               AS n
    FROM ov
)
SELECT ROUND(AVG(v), 2) AS median_order_value
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2);   -- 1 middle row if n is odd, 2 if even
"""),
    dict(
        id=38, level="Hard", topics="Pivot with conditional aggregation, YoY",
        title="Diwali month, year over year",
        prompt="Compare October 2024 vs October 2025 net revenue (valid orders) by `category`. Return `category`, "
               "`rev_oct_2024`, `rev_oct_2025` (2 dp) and `yoy_growth_pct` (1 dp); highest growth first.",
        ordered=True,
        solution="""
WITH x AS (
    SELECT p.category,
           SUM(CASE WHEN o.order_ts >= '2024-10-01' AND o.order_ts < '2024-11-01'
                    THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END) AS r24,
           SUM(CASE WHEN o.order_ts >= '2025-10-01' AND o.order_ts < '2025-11-01'
                    THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END) AS r25
    FROM order_items AS oi
    JOIN orders   AS o ON o.order_id   = oi.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY p.category
)
SELECT category,
       ROUND(r24, 2) AS rev_oct_2024,
       ROUND(r25, 2) AS rev_oct_2025,
       ROUND(100.0 * (r25 - r24) / r24, 1) AS yoy_growth_pct
FROM x
ORDER BY yoy_growth_pct DESC;
"""),
    dict(
        id=39, level="Hard", topics="Self-join for pairs (market basket)",
        title="Frequently bought together",
        prompt="Which pairs of products appear together in the same order most often (any status)? Count each pair "
               "once (lower product_id first). Return `product_a`, `product_b` (names) and `n_orders` for the top 5, "
               "ties broken by product_a then product_b name.",
        ordered=True,
        solution="""
SELECT pa.product_name AS product_a,
       pb.product_name AS product_b,
       COUNT(*)        AS n_orders
FROM order_items AS a
JOIN order_items AS b ON b.order_id = a.order_id AND a.product_id < b.product_id
JOIN products AS pa ON pa.product_id = a.product_id
JOIN products AS pb ON pb.product_id = b.product_id
GROUP BY pa.product_name, pb.product_name
ORDER BY n_orders DESC, product_a, product_b
LIMIT 5;
"""),
    dict(
        id=40, level="Hard", topics="Business question end-to-end",
        title="Do welcome coupons create loyal customers?",
        prompt="For customers whose first order (any status) was placed before **2025-07-01**, compare those whose "
               "first order used `WELCOME15` with those whose first order used no coupon. Return `first_order_type` "
               "('WELCOME15' / 'No coupon'), `n_customers` and `repeat_180d_pct` = % who placed another order within "
               "180 days of the first (1 dp). Ignore other coupon codes.",
        ordered=False,
        solution="""
WITH seq AS (
    SELECT customer_id, order_id, order_ts, coupon_code,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts, order_id) AS n
    FROM orders
), firsts AS (
    SELECT customer_id, order_ts AS first_ts,
           CASE WHEN coupon_code = 'WELCOME15' THEN 'WELCOME15'
                WHEN coupon_code IS NULL      THEN 'No coupon' END AS first_order_type
    FROM seq
    WHERE n = 1 AND order_ts < '2025-07-01'
), repeaters AS (
    SELECT DISTINCT f.customer_id
    FROM firsts AS f
    JOIN seq AS s ON s.customer_id = f.customer_id AND s.n > 1
    WHERE julianday(s.order_ts) - julianday(f.first_ts) <= 180
)
SELECT f.first_order_type,
       COUNT(*) AS n_customers,
       ROUND(100.0 * COUNT(r.customer_id) / COUNT(*), 1) AS repeat_180d_pct
FROM firsts AS f
LEFT JOIN repeaters AS r ON r.customer_id = f.customer_id
WHERE f.first_order_type IS NOT NULL
GROUP BY f.first_order_type;
"""),

    # ------------------------------------------------------------------ SET 2 (Q41–Q60)
    # New techniques: NULL counting, NTILE, pivots, recursive CTEs (date spine, hierarchy),
    # gaps-and-islands, sequence analysis, before/after validation.

    dict(set=2, id=41, level="Easy", topics="Conditional aggregation, share of total", title="Free-shipping orders",
        prompt="What share of **all** orders (any status) had no shipping fee (`shipping_fee = 0`)? Return `free_shipping_orders` and `pct_free_shipping` (1 decimal).",
        ordered=False, solution="""
SELECT SUM(shipping_fee = 0) AS free_shipping_orders,
       ROUND(100.0 * SUM(shipping_fee = 0) / COUNT(*), 1) AS pct_free_shipping
FROM orders;
"""),
    dict(set=2, id=42, level="Easy", topics="NULLs: COUNT(*) vs COUNT(column)", title="Anonymous sessions",
        prompt="In `web_sessions`, `customer_id` is NULL when the visitor wasn't logged in. Return `sessions` (all rows), `logged_in_sessions`, "
         "`anonymous_sessions` and `pct_anonymous` (1 decimal), using the difference between `COUNT(*)` and `COUNT(column)`.",
        ordered=False, solution="""
SELECT COUNT(*)                      AS sessions,
       COUNT(customer_id)            AS logged_in_sessions,
       COUNT(*) - COUNT(customer_id) AS anonymous_sessions,
       ROUND(100.0 * (COUNT(*) - COUNT(customer_id)) / COUNT(*), 1) AS pct_anonymous
FROM web_sessions;
"""),
    dict(set=2, id=43, level="Easy", topics="CASE, strftime('%w')", title="Weekend vs weekday",
        prompt="Split all orders into `Weekend` (Saturday/Sunday) and `Weekday`. Return `day_type`, `orders` and `avg_orders_per_day` "
         "(orders ÷ number of distinct calendar dates of that type that had orders, 1 decimal), weekday first.",
        ordered=True, solution="""
SELECT CASE WHEN strftime('%w', order_ts) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(*) AS orders,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT date(order_ts)), 1) AS avg_orders_per_day
FROM orders
GROUP BY day_type
ORDER BY day_type;
"""),
    dict(set=2, id=44, level="Easy", topics="strftime, GROUP BY", title="Hiring by year",
        prompt="How many employees were hired each year? Return `hire_year` and `hires`, oldest year first.",
        ordered=True, solution="""
SELECT strftime('%Y', hire_date) AS hire_year, COUNT(*) AS hires
FROM employees
GROUP BY hire_year
ORDER BY hire_year;
"""),
    dict(set=2, id=45, level="Easy", topics="CASE buckets, derived columns", title="Customers by age band",
        prompt="Using age in 2025 (`2025 - birth_year`), bucket customers into `'18-24'`, `'25-34'`, `'35-44'` and `'45+'`. "
         "Return `age_band` and `customers`, youngest band first.",
        ordered=True, solution="""
SELECT CASE WHEN 2025 - birth_year < 25 THEN '18-24'
            WHEN 2025 - birth_year < 35 THEN '25-34'
            WHEN 2025 - birth_year < 45 THEN '35-44'
            ELSE '45+' END AS age_band,
       COUNT(*) AS customers
FROM customers
GROUP BY age_band
ORDER BY age_band;
"""),
    dict(set=2, id=46, level="Easy", topics="strftime('%H'), LIMIT", title="Peak ordering hours",
        prompt="Which 3 hours of the day receive the most orders (any status)? Return `hour` (as `'00'`–`'23'`) and `orders`, busiest first.",
        ordered=True, solution="""
SELECT strftime('%H', order_ts) AS hour, COUNT(*) AS orders
FROM orders
GROUP BY hour
ORDER BY orders DESC, hour
LIMIT 3;
"""),
    dict(set=2, id=47, level="Medium", topics="Anti-join with NOT EXISTS", title="Lapsed 2024 buyers",
        prompt="Which customers placed a valid order in **2024** but **none in 2025**? Return `region` and `lapsed_customers`, most first.",
        ordered=True, solution="""
SELECT c.region, COUNT(*) AS lapsed_customers
FROM customers c
WHERE EXISTS (
        SELECT 1 FROM orders o
        WHERE o.customer_id = c.customer_id AND o.status IN ('Delivered','Shipped')
          AND o.order_ts >= '2024-01-01' AND o.order_ts < '2025-01-01')
  AND NOT EXISTS (
        SELECT 1 FROM orders o
        WHERE o.customer_id = c.customer_id AND o.status IN ('Delivered','Shipped')
          AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01')
GROUP BY c.region
ORDER BY lapsed_customers DESC;
"""),
    dict(set=2, id=48, level="Medium", topics="Pivot with conditional aggregation", title="Region × category pivot",
        prompt="Build a 2025 revenue pivot: one row per customer `region`, with columns `electronics`, `fashion`, `home_kitchen`, `other` "
         "(all remaining categories) and `total`, rounded to 2 decimals, highest total first.",
        ordered=True, solution="""
SELECT c.region,
       ROUND(SUM(CASE WHEN p.category = 'Electronics'    THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END), 2) AS electronics,
       ROUND(SUM(CASE WHEN p.category = 'Fashion'        THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END), 2) AS fashion,
       ROUND(SUM(CASE WHEN p.category = 'Home & Kitchen' THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END), 2) AS home_kitchen,
       ROUND(SUM(CASE WHEN p.category NOT IN ('Electronics','Fashion','Home & Kitchen')
                      THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END), 2) AS other,
       ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS total
FROM orders o
JOIN customers c    ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered','Shipped')
  AND o.order_ts >= '2025-01-01' AND o.order_ts < '2026-01-01'
GROUP BY c.region
ORDER BY total DESC;
"""),
    dict(set=2, id=49, level="Medium", topics="julianday, first-event logic", title="Days from sign-up to first order",
        prompt="For customers with at least one valid order, how many days pass between `signup_date` and their first valid order? "
         "Return `acquisition_channel`, `buyers` and `avg_days_to_first_order` (1 decimal), fastest channel first.",
        ordered=True, solution="""
WITH first_order AS (
    SELECT customer_id, MIN(order_ts) AS first_ts
    FROM orders
    WHERE status IN ('Delivered','Shipped')
    GROUP BY customer_id)
SELECT c.acquisition_channel,
       COUNT(*) AS buyers,
       ROUND(AVG(julianday(date(f.first_ts)) - julianday(c.signup_date)), 1) AS avg_days_to_first_order
FROM first_order f
JOIN customers c ON c.customer_id = f.customer_id
GROUP BY c.acquisition_channel
ORDER BY avg_days_to_first_order;
"""),
    dict(set=2, id=50, level="Medium", topics="Two-level aggregation, rates", title="Repeat rate by channel",
        prompt="Among customers with at least one valid order, what percentage placed **two or more** valid orders? "
         "Return `acquisition_channel`, `buyers`, `repeat_buyers`, `repeat_rate_pct` (1 decimal), highest rate first.",
        ordered=True, solution="""
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    WHERE status IN ('Delivered','Shipped')
    GROUP BY customer_id)
SELECT c.acquisition_channel,
       COUNT(*)                AS buyers,
       SUM(pc.n_orders >= 2)   AS repeat_buyers,
       ROUND(100.0 * SUM(pc.n_orders >= 2) / COUNT(*), 1) AS repeat_rate_pct
FROM per_customer pc
JOIN customers c ON c.customer_id = pc.customer_id
GROUP BY c.acquisition_channel
ORDER BY repeat_rate_pct DESC;
"""),
    dict(set=2, id=51, level="Medium", topics="NTILE, window functions", title="Spend quartiles",
        prompt="Rank buyers by lifetime valid revenue and split them into 4 equal-sized groups with `NTILE(4)` (quartile 1 = top spenders). "
         "Return `quartile`, `customers`, `min_spend`, `max_spend` and `pct_of_revenue` (1 decimal).",
        ordered=True, solution="""
WITH spend AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price - oi.discount) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status IN ('Delivered','Shipped')
    GROUP BY o.customer_id),
q AS (
    SELECT revenue, NTILE(4) OVER (ORDER BY revenue DESC, customer_id) AS quartile FROM spend)
SELECT quartile,
       COUNT(*) AS customers,
       ROUND(MIN(revenue), 2) AS min_spend,
       ROUND(MAX(revenue), 2) AS max_spend,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM spend), 1) AS pct_of_revenue
FROM q
GROUP BY quartile
ORDER BY quartile;
"""),
    dict(set=2, id=52, level="Medium", topics="Data quality: duplicates, LOWER/TRIM", title="Duplicate customer emails",
        prompt="Some people signed up twice. After normalising emails with `LOWER(TRIM(email))`, how many email addresses appear on more than one "
         "customer record, and how many records do they cover? Return `duplicated_emails` and `records_involved`.",
        ordered=False, solution="""
WITH e AS (
    SELECT LOWER(TRIM(email)) AS email, COUNT(*) AS n
    FROM customers
    WHERE email IS NOT NULL
    GROUP BY LOWER(TRIM(email))
    HAVING COUNT(*) > 1)
SELECT COUNT(*) AS duplicated_emails, SUM(n) AS records_involved
FROM e;
"""),
    dict(set=2, id=53, level="Medium", topics="Running total", title="Cumulative sign-ups in 2025",
        prompt="Show 2025 sign-ups per month and the running total. Return `month` (`YYYY-MM`), `signups`, `cumulative_signups`.",
        ordered=True, solution="""
SELECT strftime('%Y-%m', signup_date) AS month,
       COUNT(*) AS signups,
       SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', signup_date)) AS cumulative_signups
FROM customers
WHERE signup_date >= '2025-01-01' AND signup_date < '2026-01-01'
GROUP BY month
ORDER BY month;
"""),
    dict(set=2, id=54, level="Medium", topics="Conditional aggregation over time", title="Coupon share by month",
        prompt="For each month of 2025, what share of valid orders used any coupon? Return `month`, `orders`, `coupon_orders`, `coupon_pct` (1 decimal).",
        ordered=True, solution="""
SELECT strftime('%Y-%m', order_ts) AS month,
       COUNT(*) AS orders,
       COUNT(coupon_code) AS coupon_orders,
       ROUND(100.0 * COUNT(coupon_code) / COUNT(*), 1) AS coupon_pct
FROM orders
WHERE status IN ('Delivered','Shipped')
  AND order_ts >= '2025-01-01' AND order_ts < '2026-01-01'
GROUP BY month
ORDER BY month;
"""),
    dict(set=2, id=55, level="Hard", topics="Recursive CTE date spine", title="Quietest days of 2025",
        prompt="Days with **zero** orders don't appear in `orders`, so a plain GROUP BY hides them. Build a calendar of every date in 2025 "
         "with a recursive CTE, LEFT JOIN valid orders, and return the 5 dates with the fewest valid orders: `day`, `valid_orders` "
         "(fewest first, then earliest date).",
        ordered=True, solution="""
WITH RECURSIVE calendar(day) AS (
    SELECT '2025-01-01'
    UNION ALL
    SELECT date(day, '+1 day') FROM calendar WHERE day < '2025-12-31'),
daily AS (
    SELECT date(order_ts) AS day, COUNT(*) AS n
    FROM orders
    WHERE status IN ('Delivered','Shipped')
    GROUP BY date(order_ts))
SELECT c.day, COALESCE(d.n, 0) AS valid_orders
FROM calendar c
LEFT JOIN daily d ON d.day = c.day
ORDER BY valid_orders, c.day
LIMIT 5;
"""),
    dict(set=2, id=56, level="Hard", topics="Recursive CTE hierarchy", title="Org chart levels",
        prompt="Walk the reporting hierarchy with a recursive CTE, starting from the employee with no manager (level 0). "
         "Return `level`, `employees` and `avg_salary` (whole rupees) for each level, top of the org first.",
        ordered=True, solution="""
WITH RECURSIVE org(employee_id, monthly_salary, level) AS (
    SELECT employee_id, monthly_salary, 0
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.monthly_salary, org.level + 1
    FROM employees e JOIN org ON e.manager_id = org.employee_id)
SELECT level, COUNT(*) AS employees, ROUND(AVG(monthly_salary)) AS avg_salary
FROM org
GROUP BY level
ORDER BY level;
"""),
    dict(set=2, id=57, level="Hard", topics="Gaps and islands", title="Longest buying streak",
        prompt="A **streak** is a run of consecutive calendar months in which a customer placed at least one valid order. Find each customer's "
         "longest streak, then return the distribution: `streak_months` and `customers`, longest streak first.",
        ordered=True, solution="""
WITH months AS (
    SELECT DISTINCT customer_id,
           CAST(strftime('%Y', order_ts) AS INTEGER) * 12 + CAST(strftime('%m', order_ts) AS INTEGER) AS m
    FROM orders
    WHERE status IN ('Delivered','Shipped')),
islands AS (
    SELECT customer_id, m - ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY m) AS grp
    FROM months),
streaks AS (
    SELECT customer_id, COUNT(*) AS len FROM islands GROUP BY customer_id, grp),
best AS (
    SELECT customer_id, MAX(len) AS streak_months FROM streaks GROUP BY customer_id)
SELECT streak_months, COUNT(*) AS customers
FROM best
GROUP BY streak_months
ORDER BY streak_months DESC;
"""),
    dict(set=2, id=58, level="Hard", topics="Sequence analysis, EXISTS with time condition", title="Electronics buyers who come back for Fashion",
        prompt="How many customers bought **Electronics** in a valid order and then, in a **later** valid order, bought **Fashion**? "
         "Also return what percentage that is of all Electronics buyers. Columns: `electronics_buyers`, `later_fashion_buyers`, `pct` (1 decimal).",
        ordered=False, solution="""
WITH lines AS (
    SELECT o.customer_id, o.order_ts, p.category
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered','Shipped')),
first_elec AS (
    SELECT customer_id, MIN(order_ts) AS ts FROM lines WHERE category = 'Electronics' GROUP BY customer_id)
SELECT COUNT(*) AS electronics_buyers,
       SUM(EXISTS (SELECT 1 FROM lines l
                   WHERE l.customer_id = f.customer_id AND l.category = 'Fashion' AND l.order_ts > f.ts)) AS later_fashion_buyers,
       ROUND(100.0 * SUM(EXISTS (SELECT 1 FROM lines l
                   WHERE l.customer_id = f.customer_id AND l.category = 'Fashion' AND l.order_ts > f.ts)) / COUNT(*), 1) AS pct
FROM first_elec f;
"""),
    dict(set=2, id=59, level="Hard", topics="Before/after comparison, data validation", title="Did the April 2025 price rise stick?",
        prompt="Finance says every price went up **5% on 2025-04-01**. Check it: for each product sold (valid orders) both in "
         "2025-01-01…2025-03-31 and in 2025-04-01…2025-06-30, compute its average `unit_price` in each period and the % change. "
         "Then summarise by category: `category`, `products`, `min_pct_change`, `max_pct_change` (1 decimal), alphabetical by category. "
         "(Bonus: a few products rose slightly *less* than 5%. Look at their prices: why might that be?)",
        ordered=True, solution="""
WITH per_product AS (
    SELECT p.category, p.product_id,
           AVG(CASE WHEN o.order_ts <  '2025-04-01' THEN oi.unit_price END) AS before_price,
           AVG(CASE WHEN o.order_ts >= '2025-04-01' THEN oi.unit_price END) AS after_price
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered','Shipped')
      AND o.order_ts >= '2025-01-01' AND o.order_ts < '2025-07-01'
    GROUP BY p.category, p.product_id)
SELECT category,
       COUNT(*) AS products,
       ROUND(MIN(100.0 * (after_price / before_price - 1)), 1) AS min_pct_change,
       ROUND(MAX(100.0 * (after_price / before_price - 1)), 1) AS max_pct_change
FROM per_product
WHERE before_price IS NOT NULL AND after_price IS NOT NULL
GROUP BY category
ORDER BY category;
"""),
    dict(set=2, id=60, level="Hard", topics="YoY growth + RANK", title="Fastest-growing categories",
        prompt="Compare valid revenue in 2024 and 2025 for each category. Return `category`, `revenue_2024`, `revenue_2025` (whole rupees), "
         "`yoy_growth_pct` (1 decimal) and `growth_rank` (1 = fastest, using RANK), ordered by rank.",
        ordered=True, solution="""
WITH yearly AS (
    SELECT p.category,
           SUM(CASE WHEN o.order_ts < '2025-01-01' THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END) AS r24,
           SUM(CASE WHEN o.order_ts >= '2025-01-01' THEN oi.quantity * oi.unit_price - oi.discount ELSE 0 END) AS r25
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered','Shipped')
      AND o.order_ts >= '2024-01-01' AND o.order_ts < '2026-01-01'
    GROUP BY p.category)
SELECT category,
       ROUND(r24) AS revenue_2024,
       ROUND(r25) AS revenue_2025,
       ROUND(100.0 * (r25 - r24) / r24, 1) AS yoy_growth_pct,
       RANK() OVER (ORDER BY (r25 - r24) / r24 DESC) AS growth_rank
FROM yearly
ORDER BY growth_rank;
"""),
]
