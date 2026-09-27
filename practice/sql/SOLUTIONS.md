# SQL Practice — Reference solutions

Try each question first! Many have more than one correct approach — `check.py` compares *results*, not query text.


## Easy

### Q01 — Premium electronics

```sql
SELECT product_name, list_price
FROM products
WHERE category = 'Electronics'
  AND list_price > 2000
ORDER BY list_price DESC;
```

<details><summary>Expected output</summary>

| product_name | list_price |
|---|---|
| Smartwatch | 4,999.00 |
| Mechanical Keyboard | 3,999.00 |
| Over-Ear Headphones | 3,499.00 |
| Bluetooth Speaker | 2,499.00 |
| Fitness Band | 2,299.00 |

</details>

### Q02 — 2025 sign-ups

```sql
SELECT COUNT(*) AS signups_2025
FROM customers
WHERE signup_date >= '2025-01-01'
  AND signup_date <  '2026-01-01';
```

<details><summary>Expected output</summary>

| signups_2025 |
|---|
| 4781 |

</details>

### Q03 — Orders by status

```sql
SELECT status, COUNT(*) AS n_orders
FROM orders
GROUP BY status
ORDER BY n_orders DESC;
```

<details><summary>Expected output</summary>

| status | n_orders |
|---|---|
| Delivered | 10013 |
| Returned | 1101 |
| Cancelled | 659 |
| Shipped | 112 |

</details>

### Q04 — Top 5 cities

```sql
SELECT city, COUNT(*) AS n_customers
FROM customers
GROUP BY city
ORDER BY n_customers DESC
LIMIT 5;
```

<details><summary>Expected output</summary>

| city | n_customers |
|---|---|
| Delhi | 1141 |
| Bengaluru | 1057 |
| Mumbai | 1027 |
| Hyderabad | 612 |
| Pune | 601 |

</details>

### Q05 — Payment mix

```sql
SELECT payment_method,
       COUNT(*) AS n_orders,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS pct_orders
FROM orders
GROUP BY payment_method
ORDER BY n_orders DESC;
```

<details><summary>Expected output</summary>

| payment_method | n_orders | pct_orders |
|---|---|---|
| UPI | 5498 | 46.30 |
| Cash on Delivery | 2332 | 19.60 |
| Credit Card | 2096 | 17.60 |
| Debit Card | 1239 | 10.40 |
| Net Banking | 720 | 6.10 |

</details>

### Q06 — Yahoo users

```sql
SELECT COUNT(*) AS n_customers
FROM customers
WHERE email LIKE '%@yahoo.in';
```

<details><summary>Expected output</summary>

| n_customers |
|---|
| 1004 |

</details>

### Q07 — Price range per category

```sql
SELECT category,
       ROUND(AVG(list_price), 2) AS avg_price,
       MIN(list_price)           AS min_price,
       MAX(list_price)           AS max_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;
```

<details><summary>Expected output</summary>

| category | avg_price | min_price | max_price |
|---|---|---|---|
| Electronics | 2,319.00 | 399.00 | 4,999.00 |
| Sports | 1,815.67 | 599.00 | 4,499.00 |
| Fashion | 1,779.00 | 499.00 | 3,999.00 |
| Home & Kitchen | 1,449.00 | 449.00 | 3,299.00 |
| Beauty | 586.50 | 199.00 | 1,499.00 |
| Books | 479.00 | 249.00 | 799.00 |

</details>

### Q08 — Coupon usage

```sql
SELECT CASE WHEN coupon_code IS NULL THEN 'No' ELSE 'Yes' END AS coupon_used,
       COUNT(*) AS n_orders
FROM orders
GROUP BY coupon_used;
```

<details><summary>Expected output</summary>

| coupon_used | n_orders |
|---|---|
| No | 7674 |
| Yes | 4211 |

</details>

### Q09 — Total net revenue

```sql
SELECT ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS total_net_revenue
FROM order_items AS oi
JOIN orders      AS o ON o.order_id = oi.order_id
WHERE o.status IN ('Delivered', 'Shipped');
```

<details><summary>Expected output</summary>

| total_net_revenue |
|---|
| 30,531,948.30 |

</details>

### Q10 — Monthly orders in 2025

```sql
SELECT strftime('%Y-%m', order_ts) AS month,
       COUNT(*) AS n_orders
FROM orders
WHERE order_ts >= '2025-01-01' AND order_ts < '2026-01-01'
GROUP BY month
ORDER BY month;
```

<details><summary>Expected output</summary>

| month | n_orders |
|---|---|
| 2025-01 | 488 |
| 2025-02 | 437 |
| 2025-03 | 522 |
| 2025-04 | 537 |
| 2025-05 | 595 |
| 2025-06 | 585 |
| … 6 more rows | |

</details>

### Q11 — October 2025 orders

```sql
-- BETWEEN '2025-10-01' AND '2025-10-31' would silently drop everything
-- placed on 31 Oct after midnight. Use a half-open range instead.
SELECT COUNT(*) AS n_orders
FROM orders
WHERE order_ts >= '2025-10-01'
  AND order_ts <  '2025-11-01';
```

<details><summary>Expected output</summary>

| n_orders |
|---|
| 1221 |

</details>

### Q12 — Well-paid analysts

```sql
SELECT full_name, monthly_salary
FROM employees
WHERE department = 'Analytics'
  AND monthly_salary >= 100000
ORDER BY monthly_salary DESC, full_name;
```

<details><summary>Expected output</summary>

| full_name | monthly_salary |
|---|---|
| Sunita Rao | 260000 |
| Neha Gupta | 140000 |
| Karan Malhotra | 110000 |

</details>


## Medium

### Q13 — Revenue by category

```sql
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price - oi.discount), 2) AS net_revenue
FROM order_items AS oi
JOIN orders      AS o ON o.order_id  = oi.order_id
JOIN products    AS p ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY net_revenue DESC;
```

<details><summary>Expected output</summary>

| category | net_revenue |
|---|---|
| Electronics | 10,739,754.90 |
| Fashion | 9,676,082.05 |
| Home & Kitchen | 5,313,647.90 |
| Sports | 2,206,985.40 |
| Beauty | 1,939,934.25 |
| Books | 655,543.80 |

</details>

### Q14 — Signed up, never ordered

```sql
SELECT COUNT(*) AS n_customers
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- Equivalent: WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
```

<details><summary>Expected output</summary>

| n_customers |
|---|
| 1770 |

</details>

### Q15 — Top 10 customers

```sql
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
```

<details><summary>Expected output</summary>

| customer_id | customer_name | n_orders | net_revenue |
|---|---|---|---|
| 10345 | Farhan Kumar | 11 | 42,830.00 |
| 13002 | Sneha Patel | 7 | 40,171.15 |
| 11927 | Kiara Chopra | 8 | 38,594.45 |
| 11819 | Manish Kumar | 7 | 37,129.35 |
| 10275 | Deepak Mishra | 9 | 36,458.05 |
| 12006 | Aarav Verma | 6 | 35,181.40 |
| … 4 more rows | | | |

</details>

### Q16 — AOV by device

```sql
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
```

<details><summary>Expected output</summary>

| device | n_orders | aov |
|---|---|---|
| Desktop | 2055 | 3,041.17 |
| Mobile App | 5051 | 3,035.49 |
| Mobile Web | 3019 | 2,964.59 |

</details>

### Q17 — Return rate by category

```sql
SELECT p.category,
       COUNT(*) AS n_lines,
       ROUND(100.0 * SUM(CASE WHEN o.status = 'Returned' THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM order_items AS oi
JOIN orders   AS o ON o.order_id   = oi.order_id
JOIN products AS p ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Returned')
GROUP BY p.category
ORDER BY return_rate_pct DESC;
```

<details><summary>Expected output</summary>

| category | n_lines | return_rate_pct |
|---|---|---|
| Fashion | 5893 | 16.00 |
| Sports | 1282 | 10.10 |
| Electronics | 4174 | 9.30 |
| Home & Kitchen | 3480 | 8.70 |
| Beauty | 2966 | 7.80 |
| Books | 1216 | 7.50 |

</details>

### Q18 — Cancellations by payment method

```sql
SELECT payment_method,
       COUNT(*) AS n_orders,
       ROUND(100.0 * AVG(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END), 1) AS cancel_rate_pct
FROM orders
GROUP BY payment_method
ORDER BY cancel_rate_pct DESC;
```

<details><summary>Expected output</summary>

| payment_method | n_orders | cancel_rate_pct |
|---|---|---|
| Cash on Delivery | 2332 | 11.70 |
| Debit Card | 1239 | 4.90 |
| Net Banking | 720 | 4.30 |
| UPI | 5498 | 3.90 |
| Credit Card | 2096 | 3.70 |

</details>

### Q19 — Gross margin by category

```sql
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
```

<details><summary>Expected output</summary>

| category | net_revenue | cogs | gross_margin_pct |
|---|---|---|---|
| Beauty | 1,939,934.25 | 863,646.82 | 55.50 |
| Fashion | 9,676,082.05 | 4,567,654.11 | 52.80 |
| Sports | 2,206,985.40 | 1,363,883.79 | 38.20 |
| Home & Kitchen | 5,313,647.90 | 3,570,425.40 | 32.80 |
| Books | 655,543.80 | 472,710.10 | 27.90 |
| Electronics | 10,739,754.90 | 8,583,759.25 | 20.10 |

</details>

### Q20 — Who reports to whom

```sql
SELECT e.full_name AS employee,
       m.full_name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.employee_id = e.manager_id
ORDER BY e.employee_id;
```

<details><summary>Expected output</summary>

| employee | manager |
|---|---|
| Rajesh Khanna | NULL |
| Sunita Rao | Rajesh Khanna |
| Imran Qureshi | Rajesh Khanna |
| Lakshmi Iyer | Rajesh Khanna |
| Arvind Menon | Rajesh Khanna |
| Neha Gupta | Sunita Rao |
| … 24 more rows | |

</details>

### Q21 — Second-highest salary

```sql
SELECT MAX(monthly_salary) AS second_highest_salary
FROM employees
WHERE monthly_salary < (SELECT MAX(monthly_salary) FROM employees);

-- Window-function version (generalises to Nth highest):
-- SELECT DISTINCT monthly_salary FROM (
--   SELECT monthly_salary, DENSE_RANK() OVER (ORDER BY monthly_salary DESC) AS rnk FROM employees
-- ) WHERE rnk = 2;
```

<details><summary>Expected output</summary>

| second_highest_salary |
|---|
| 300000 |

</details>

### Q22 — Top earner per department

```sql
WITH ranked AS (
    SELECT department, full_name, monthly_salary,
           RANK() OVER (PARTITION BY department ORDER BY monthly_salary DESC) AS rnk
    FROM employees
)
SELECT department, full_name, monthly_salary
FROM ranked
WHERE rnk = 1
ORDER BY department, full_name;
```

<details><summary>Expected output</summary>

| department | full_name | monthly_salary |
|---|---|---|
| Analytics | Sunita Rao | 260000 |
| Customer Support | Harpreet Gill | 90000 |
| Engineering | Arvind Menon | 300000 |
| Leadership | Rajesh Khanna | 450000 |
| Marketing | Imran Qureshi | 240000 |
| Operations | Lakshmi Iyer | 230000 |

</details>

### Q23 — Customers active in both years

```sql
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
```

<details><summary>Expected output</summary>

| n_customers |
|---|
| 713 |

</details>

### Q24 — Best seller in each category

```sql
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
```

<details><summary>Expected output</summary>

| category | product_name | units_sold |
|---|---|---|
| Beauty | Hair Oil | 632 |
| Books | Competitive Exam Guide | 353 |
| Electronics | 65W Fast Charger | 698 |
| Fashion | Cotton T-Shirt | 838 |
| Home & Kitchen | Diya & Candle Set | 721 |
| Sports | Yoga Mat | 335 |

</details>

### Q25 — Month-over-month growth

```sql
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
```

<details><summary>Expected output</summary>

| month | net_revenue | prev_month_revenue | mom_growth_pct |
|---|---|---|---|
| 2024-01 | 358,568.80 | NULL | NULL |
| 2024-02 | 597,694.30 | 358,568.80 | 66.70 |
| 2024-03 | 605,689.90 | 597,694.30 | 1.30 |
| 2024-04 | 686,462.70 | 605,689.90 | 13.30 |
| 2024-05 | 836,336.95 | 686,462.70 | 21.80 |
| 2024-06 | 896,526.50 | 836,336.95 | 7.20 |
| … 18 more rows | | | |

</details>

### Q26 — 2025 revenue, cumulative

```sql
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
```

<details><summary>Expected output</summary>

| month | net_revenue | running_total |
|---|---|---|
| 2025-01 | 1,138,689.35 | 1,138,689.35 |
| 2025-02 | 1,019,542.50 | 2,158,231.85 |
| 2025-03 | 1,314,976.55 | 3,473,208.40 |
| 2025-04 | 1,434,515.25 | 4,907,723.65 |
| 2025-05 | 1,680,767.90 | 6,588,491.55 |
| 2025-06 | 1,462,084.30 | 8,050,575.85 |
| … 6 more rows | | |

</details>

### Q27 — Time to second order

```sql
WITH seq AS (
    SELECT customer_id, order_ts,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_ts, order_id) AS n
    FROM orders
)
SELECT ROUND(AVG(julianday(s2.order_ts) - julianday(s1.order_ts)), 1) AS avg_days_to_second_order
FROM seq AS s1
JOIN seq AS s2 ON s2.customer_id = s1.customer_id AND s2.n = 2
WHERE s1.n = 1;
```

<details><summary>Expected output</summary>

| avg_days_to_second_order |
|---|
| 82.60 |

</details>

### Q28 — Conversion funnel by device

```sql
SELECT device,
       COUNT(*) AS sessions,
       ROUND(100.0 * AVG(viewed_product), 1) AS product_view_pct,
       ROUND(100.0 * AVG(added_to_cart), 1)  AS add_to_cart_pct,
       ROUND(100.0 * AVG(began_checkout), 1) AS checkout_pct,
       ROUND(100.0 * AVG(purchased), 1)      AS purchase_pct
FROM web_sessions
GROUP BY device
ORDER BY purchase_pct DESC;
```

<details><summary>Expected output</summary>

| device | sessions | product_view_pct | add_to_cart_pct | checkout_pct | purchase_pct |
|---|---|---|---|---|---|
| Mobile App | 20041 | 72.40 | 28.20 | 19.00 | 14.00 |
| Desktop | 7976 | 66.00 | 20.40 | 12.70 | 9.00 |
| Mobile Web | 11983 | 59.80 | 15.90 | 8.60 | 4.90 |

</details>


## Hard

### Q29 — New vs returning revenue

```sql
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
```

<details><summary>Expected output</summary>

| month | new_customer_revenue | returning_customer_revenue |
|---|---|---|
| 2025-01 | 624,924.75 | 513,764.60 |
| 2025-02 | 497,466.70 | 522,075.80 |
| 2025-03 | 701,868.70 | 613,107.85 |
| 2025-04 | 692,384.60 | 742,130.65 |
| 2025-05 | 854,088.10 | 826,679.80 |
| 2025-06 | 733,988.15 | 728,096.15 |
| … 6 more rows | | |

</details>

### Q30 — Monthly cohort retention

```sql
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
```

<details><summary>Expected output</summary>

| cohort_month | cohort_size | m1_pct | m2_pct | m3_pct |
|---|---|---|---|---|
| 2025-01 | 257 | 15.20 | 14.40 | 10.90 |
| 2025-02 | 234 | 15.00 | 13.20 | 8.10 |
| 2025-03 | 281 | 14.20 | 15.30 | 7.80 |
| 2025-04 | 272 | 15.40 | 13.20 | 11.40 |
| 2025-05 | 298 | 17.40 | 15.80 | 10.40 |
| 2025-06 | 292 | 15.40 | 11.60 | 9.90 |

</details>

### Q31 — 3-month moving average

```sql
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
```

<details><summary>Expected output</summary>

| month | net_revenue | ma_3m |
|---|---|---|
| 2024-01 | 358,568.80 | 358,568.80 |
| 2024-02 | 597,694.30 | 478,131.55 |
| 2024-03 | 605,689.90 | 520,651.00 |
| 2024-04 | 686,462.70 | 629,948.97 |
| 2024-05 | 836,336.95 | 709,496.52 |
| 2024-06 | 896,526.50 | 806,442.05 |
| … 18 more rows | | |

</details>

### Q32 — The 80/20 rule

```sql
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
```

<details><summary>Expected output</summary>

| n_customers_for_80pct | pct_of_buyers |
|---|---|
| 2598 | 45.70 |

</details>

### Q33 — Rule-based customer segments

```sql
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
```

<details><summary>Expected output</summary>

| segment | n_customers | avg_revenue |
|---|---|---|
| Lapsed One-timer | 2386 | 2,917.50 |
| At Risk | 1127 | 8,269.07 |
| Loyal | 1091 | 7,439.95 |
| New | 843 | 3,129.11 |
| Champion | 233 | 15,007.47 |

</details>

### Q34 — Find the operational incident

```sql
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
```

<details><summary>Expected output</summary>

| state | month | n_orders | cancel_rate_pct |
|---|---|---|---|
| Maharashtra | 2025-06 | 111 | 30.60 |

</details>

### Q35 — A/B test summary

```sql
SELECT variant, device,
       COUNT(*)                              AS visitors,
       SUM(converted)                        AS conversions,
       ROUND(100.0 * AVG(converted), 2)      AS conv_rate_pct,
       ROUND(AVG(order_value), 2)            AS revenue_per_visitor
FROM checkout_experiment
GROUP BY variant, device
ORDER BY device, variant;
```

<details><summary>Expected output</summary>

| variant | device | visitors | conversions | conv_rate_pct | revenue_per_visitor |
|---|---|---|---|---|---|
| A_control | Desktop | 2347 | 252 | 10.74 | 153.85 |
| B_new_checkout | Desktop | 2335 | 241 | 10.32 | 141.09 |
| A_control | Mobile App | 5379 | 610 | 11.34 | 162.30 |
| B_new_checkout | Mobile App | 5465 | 796 | 14.57 | 202.93 |
| A_control | Mobile Web | 4280 | 380 | 8.88 | 129.99 |
| B_new_checkout | Mobile Web | 4194 | 377 | 8.99 | 126.26 |

</details>

### Q36 — Longest gap between orders

```sql
WITH gaps AS (
    SELECT customer_id,
           julianday(order_ts)
             - julianday(LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts, order_id)) AS gap
    FROM orders
)
SELECT CAST(MAX(gap) AS INTEGER) AS max_gap_days
FROM gaps;
```

<details><summary>Expected output</summary>

| max_gap_days |
|---|
| 650 |

</details>

### Q37 — Median order value

```sql
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
```

<details><summary>Expected output</summary>

| median_order_value |
|---|
| 2,297.00 |

</details>

### Q38 — Diwali month, year over year

```sql
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
```

<details><summary>Expected output</summary>

| category | rev_oct_2024 | rev_oct_2025 | yoy_growth_pct |
|---|---|---|---|
| Sports | 79,402.85 | 215,315.75 | 171.20 |
| Home & Kitchen | 271,502.70 | 712,516.85 | 162.40 |
| Fashion | 444,705.80 | 1,032,429.60 | 132.20 |
| Electronics | 515,783.45 | 1,076,993.85 | 108.80 |
| Beauty | 90,661.75 | 178,913.50 | 97.30 |
| Books | 39,635.75 | 60,299.25 | 52.10 |

</details>

### Q39 — Frequently bought together

```sql
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
```

<details><summary>Expected output</summary>

| product_a | product_b | n_orders |
|---|---|---|
| Casual Sandals | Diya & Candle Set | 50 |
| Linen Shirt | Anarkali Dress | 49 |
| Cotton T-Shirt | Casual Sandals | 46 |
| Linen Shirt | Casual Sandals | 46 |
| Slim Fit Jeans | Diya & Candle Set | 46 |

</details>

### Q40 — Do welcome coupons create loyal customers?

```sql
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
```

<details><summary>Expected output</summary>

| first_order_type | n_customers | repeat_180d_pct |
|---|---|---|
| No coupon | 2009 | 48.40 |
| WELCOME15 | 1860 | 44.90 |

</details>

