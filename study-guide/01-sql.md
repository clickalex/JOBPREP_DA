# 01 · SQL for data analyst interviews

SQL is the one skill that almost *every* data analyst interview tests, usually as a live coding round or a
timed online test (HackerRank, CodeSignal, TestGorilla, or a shared Google Doc). Aim to solve Medium questions in about
10 minutes, talking through your thinking as you go.

**Practice:** [40 graded questions](../practice/sql/EXERCISES.md) on the ShopKart database · `python practice/sql/check.py`

---

## 1. How a query is actually executed

You *write* `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`, but the database *evaluates* it in this order:

```
FROM / JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT (incl. window functions)  →  DISTINCT  →  ORDER BY  →  LIMIT
```

This order explains most "why doesn't this work?" moments:

* You **can't use a SELECT alias in WHERE**, because WHERE runs before SELECT. (Many engines, SQLite included, *do* allow aliases in GROUP BY and ORDER BY.)
* You **can't filter on a window function in WHERE.** Wrap it in a CTE or subquery, then filter.
* **WHERE filters rows before grouping; HAVING filters groups after.** `WHERE SUM(x) > 10` is an error; use `HAVING SUM(x) > 10`.

## 2. Joins

| Join | Returns | Typical use |
|---|---|---|
| `INNER JOIN` | only matching rows from both sides | orders with their customers |
| `LEFT JOIN` | all left rows + matches (NULLs where none) | customers *and* their orders, including customers with none |
| `RIGHT JOIN` | mirror of LEFT (rarely used, so rewrite as LEFT) | |
| `FULL OUTER JOIN` | all rows from both sides | reconciling two sources |
| `CROSS JOIN` | every combination | building a date × category grid |
| Self join | a table joined to itself | employee → manager, consecutive events |

**Anti-join (rows with NO match)**, the classic *"customers who never ordered"*:

```sql
SELECT c.*
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;          -- or: WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
```

⚠️ **Avoid `NOT IN (subquery)` if the subquery can return NULL.** `x NOT IN (1, NULL)` is never true, so it silently returns zero rows.

⚠️ **LEFT JOIN turned into an INNER JOIN.** A filter on the *right* table in `WHERE` removes the NULL rows:

```sql
-- WRONG: drops customers without 2025 orders
SELECT c.customer_id, COUNT(o.order_id)
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_ts >= '2025-01-01'
GROUP BY c.customer_id;

-- RIGHT: put the condition in the ON clause
... LEFT JOIN orders o ON o.customer_id = c.customer_id AND o.order_ts >= '2025-01-01'
```

⚠️ **Fan-out / double counting.** Joining orders (1) to order_items (many) repeats each order once per line.
`COUNT(*)` then counts lines, not orders, and `SUM(shipping_fee)` gets inflated. Use `COUNT(DISTINCT o.order_id)`, or
aggregate the many-side in a CTE *before* joining.

**Quick sanity check:** know each table's **grain** (what one row represents) before joining. After a join, compare
`COUNT(*)` with what you expected.

## 3. Aggregation & NULLs

* `COUNT(*)` counts rows; `COUNT(col)` counts **non-NULL** values; `COUNT(DISTINCT col)` counts unique non-NULL values.
* `SUM`, `AVG`, `MIN` and `MAX` **ignore NULLs**. `AVG(col)` is *not* `SUM(col)/COUNT(*)` when NULLs exist.
* `NULL = NULL` is not true (it's NULL). Use `IS NULL` / `IS NOT NULL`, and `COALESCE(col, 0)` to substitute.
* **Integer division:** `1/2 = 0` in SQLite, PostgreSQL and SQL Server. Write `100.0 * a / b` or `CAST(a AS FLOAT)`.
* **Divide-by-zero:** `a / NULLIF(b, 0)` returns NULL instead of an error.

**Conditional aggregation** is the single most useful interview pattern. It gives you pivots, rates and multiple
metrics in one pass:

```sql
SELECT payment_method,
       COUNT(*)                                                   AS orders,
       SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)       AS cancelled,
       ROUND(100.0 * AVG(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END), 1) AS cancel_rate_pct
FROM orders
GROUP BY payment_method;
```

## 4. Subqueries vs CTEs

```sql
WITH order_value AS (                 -- a CTE: a named, readable step
    SELECT order_id, SUM(quantity * unit_price - discount) AS value
    FROM order_items GROUP BY order_id
)
SELECT AVG(value) FROM order_value;
```

* CTEs make multi-step logic readable. **In interviews, prefer CTEs** and name each step for what it *means*.
* A **correlated subquery** re-runs for each outer row (`WHERE salary > (SELECT AVG(salary) FROM employees e2 WHERE e2.department = e1.department)`). It's readable, but a window function is usually faster.
* **Recursive CTEs** walk hierarchies (org charts) or generate series. It's worth knowing they exist.

## 5. Window functions (the most-tested advanced topic)

A window function computes across a set of rows related to the current row **without collapsing them** (unlike GROUP BY).

```sql
function() OVER (PARTITION BY <group> ORDER BY <sort> [ROWS BETWEEN … AND …])
```

| Family | Functions | Example question |
|---|---|---|
| Ranking | `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE(n)` | top product per category; Nth highest salary |
| Offset | `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE` | MoM growth; days between orders |
| Aggregate | `SUM`, `AVG`, `COUNT`, `MIN`, `MAX` … `OVER` | running total; moving average; % of total |

**ROW_NUMBER vs RANK vs DENSE_RANK** for salaries 100, 90, 90, 80:

| salary | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 80 | 4 | **4** | **3** |

"Nth highest *distinct* salary" → `DENSE_RANK`. "Exactly one row per group" → `ROW_NUMBER` (add a tie-breaker to ORDER BY).

**Frames:** with an `ORDER BY`, aggregate windows default to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
That's a running total, but tied ORDER BY values are summed together. Be explicit:

```sql
SUM(revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)  -- running total
AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)          -- 3-period moving avg
revenue / SUM(revenue) OVER ()                                                        -- share of grand total
revenue / SUM(revenue) OVER (PARTITION BY category)                                   -- share within group
```

⚠️ `LAST_VALUE` with the default frame returns the *current* row. Use `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

## 6. Patterns worth memorising

**Top-N per group**
```sql
WITH r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn FROM product_revenue)
SELECT * FROM r WHERE rn <= 3;
```

**De-duplicate (keep the latest row per key)**
```sql
WITH r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email ORDER BY updated_at DESC) AS rn FROM users)
SELECT * FROM r WHERE rn = 1;
```

**Period-over-period growth**
```sql
SELECT month, revenue,
       100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) AS mom_pct
FROM monthly;
```

**First/second event per user** → `ROW_NUMBER() OVER (PARTITION BY user ORDER BY ts)`, then filter `rn = 1` / `rn = 2`, or use `LEAD`.

**Cohort retention** → cohort = first activity month; `month_n` = months between activity and cohort; count distinct users per (cohort, month_n); divide by the month-0 count. (See practice Q30.)

**Gaps & islands (consecutive-day streaks)** → `date - ROW_NUMBER() OVER (PARTITION BY user ORDER BY date)` is constant within a streak; group by it.

**Median** (no MEDIAN function in SQLite/MySQL) → `ROW_NUMBER()` + `COUNT(*) OVER ()`, keep the middle row(s). PostgreSQL: `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x)`.

**Pivot** → conditional aggregation: `SUM(CASE WHEN year = 2025 THEN revenue END) AS rev_2025`.

**Date ranges with timestamps** → half-open intervals: `ts >= '2025-10-01' AND ts < '2025-11-01'`.
`BETWEEN '2025-10-01' AND '2025-10-31'` misses everything after midnight on the 31st.

## 7. Dialect cheat sheet

| Task | SQLite (this repo) | PostgreSQL | MySQL | SQL Server |
|---|---|---|---|---|
| Month bucket | `strftime('%Y-%m', ts)` | `DATE_TRUNC('month', ts)` | `DATE_FORMAT(ts, '%Y-%m-01')` | `DATETRUNC(month, ts)` (2022+) / `FORMAT(ts,'yyyy-MM')` |
| Extract year | `strftime('%Y', ts)` | `EXTRACT(YEAR FROM ts)` | `YEAR(ts)` | `YEAR(ts)` |
| Days between | `julianday(b) - julianday(a)` | `b::date - a::date` | `DATEDIFF(b, a)` | `DATEDIFF(day, a, b)` |
| Add interval | `date(ts, '+7 day')` | `ts + INTERVAL '7 days'` | `DATE_ADD(ts, INTERVAL 7 DAY)` | `DATEADD(day, 7, ts)` |
| Today | `date('now')` | `CURRENT_DATE` | `CURDATE()` | `CAST(GETDATE() AS date)` |
| Concatenate | `a \|\| b` | `a \|\| b` / `CONCAT` | `CONCAT(a, b)` | `a + b` / `CONCAT` |
| First N rows | `LIMIT n` | `LIMIT n` | `LIMIT n` | `TOP n` / `FETCH FIRST n ROWS ONLY` |
| NULL substitute | `IFNULL` / `COALESCE` | `COALESCE` | `IFNULL` / `COALESCE` | `ISNULL` / `COALESCE` |
| Median | manual | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x)` | manual | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) OVER ()` |
| Case-insensitive match | `LIKE` (ASCII) | `ILIKE` | `LIKE` (default collation) | `LIKE` (default collation) |

BigQuery and Snowflake are close to PostgreSQL (`DATE_TRUNC`, `DATE_DIFF` / `DATEDIFF`, `QUALIFY` to filter window
functions directly).

## 8. Performance basics (junior level)

* Select only the columns you need; avoid `SELECT *` on wide tables.
* Filter early; filter on **indexed** columns *without wrapping them in functions*. `WHERE order_ts >= '2025-01-01'` can use an index; `WHERE strftime('%Y', order_ts) = '2025'` can't (not "sargable").
* `EXISTS` often beats `IN` for large subqueries; `UNION ALL` beats `UNION` when duplicates don't matter (no de-dup sort).
* `EXPLAIN` / `EXPLAIN QUERY PLAN` shows whether an index is used.

## 9. How to run a live SQL round

1. **Clarify** the grain, the definitions ("does revenue include cancelled orders?"), ties, NULLs and the expected output.
2. **Say your plan** in steps ("first I'll get each customer's first order, then…"), and write CTEs in that order.
3. **Check on a small case.** Eyeball row counts and look for fan-out.
4. **Mention edge cases** (ties, NULLs, customers with one order) and how you'd productionise (indexes, incremental loads).

## 10. Conceptual questions they ask

<details><summary><b>WHERE vs HAVING?</b></summary>WHERE filters rows before aggregation; HAVING filters aggregated groups. Use WHERE where possible; it's cheaper.</details>
<details><summary><b>UNION vs UNION ALL?</b></summary>UNION removes duplicates (extra sort/hash); UNION ALL keeps everything and is faster.</details>
<details><summary><b>DELETE vs TRUNCATE vs DROP?</b></summary>DELETE removes chosen rows (logged, can use WHERE, can roll back); TRUNCATE empties the table quickly; DROP removes the table itself.</details>
<details><summary><b>Primary key vs unique key vs foreign key?</b></summary>PK uniquely identifies a row (not NULL, one per table); a UNIQUE constraint also enforces uniqueness but allows NULL (engine-dependent) and there can be many; a FK references another table's key to enforce referential integrity.</details>
<details><summary><b>What is normalization? When would you denormalize?</b></summary>Organising tables to reduce redundancy (1NF atomic values, 2NF no partial dependency, 3NF no transitive dependency). Analytics warehouses often denormalize into star schemas / wide tables for simpler, faster reads.</details>
<details><summary><b>What is an index and what's the trade-off?</b></summary>A sorted lookup structure (usually a B-tree) that speeds up reads and joins on its columns, at the cost of storage and slower writes.</details>
<details><summary><b>CTE vs temp table vs view?</b></summary>A CTE exists for one statement; a temp table persists for the session and can be indexed; a view is a saved query (a materialized view also stores the results).</details>
<details><summary><b>ROW_NUMBER vs RANK vs DENSE_RANK?</b></summary>See the table in section 5: ROW_NUMBER is always unique, RANK leaves gaps after ties, DENSE_RANK doesn't.</details>
<details><summary><b>How do you find duplicates?</b></summary><code>GROUP BY key HAVING COUNT(*) &gt; 1</code>, or <code>ROW_NUMBER() OVER (PARTITION BY key …) &gt; 1</code> to find/delete all but one.</details>
<details><summary><b>COUNT(*) vs COUNT(1) vs COUNT(col)?</b></summary>COUNT(*) and COUNT(1) are equivalent (count rows); COUNT(col) skips NULLs.</details>
<details><summary><b>What's a fact vs a dimension table?</b></summary>Facts hold measurable events at a defined grain (order lines, with amounts); dimensions describe them (customer, product, date). See the <a href="05-bi-powerbi-tableau.md">BI guide</a>.</details>
<details><summary><b>OLTP vs OLAP?</b></summary>OLTP systems handle many small transactional reads/writes (the app's database, normalized). OLAP systems handle large analytical scans (the warehouse: columnar, denormalized).</details>
