# 05 · BI tools: Power BI & Tableau

Most DA job descriptions in India ask for **Power BI** (the most common, especially in services and enterprise) or
**Tableau** (common in product and consulting firms). Learn one deeply and understand the other's concepts.
Interviews cover data modelling, DAX / calculated fields, dashboard design and a portfolio walkthrough.

**Practice:** build the [ShopKart dashboard](../portfolio/shopkart-growth-analysis/dashboard/README.md). It includes the star-schema CSVs, 15+ DAX measures, Tableau equivalents and target numbers to check against.

---

## 1. Data modelling (tool-agnostic, asked everywhere)

* **Fact table**: events/transactions at a declared **grain** ("one row per order line"), with numeric measures and foreign keys.
* **Dimension tables**: descriptive attributes to slice by (customer, product, date, store). One row per key.
* **Star schema**: facts in the middle, dimensions around them, one-to-many relationships. The preferred model for BI: simple, fast and unambiguous. *Snowflake* = dimensions normalised into sub-dimensions (more joins, rarely worth it in BI).
* **Date dimension**: one row per day, no gaps, with year, month, quarter, fiscal year (India: April–March), weekday and holiday flags. Required for time intelligence.
* **Cardinality**: one-to-many (normal), many-to-many (avoid; use a bridge table), one-to-one (usually merge the tables).
* **Slowly changing dimensions (SCD)**: Type 1 overwrites history; Type 2 adds a new row with valid-from/valid-to dates (e.g. a customer moving city).

## 2. Power BI

### Workflow
**Power Query** (extract & transform, M language) → **Model** (relationships, DAX measures) → **Report** (visuals) → **Service** (publish, schedule refresh, workspaces, apps, row-level security).

### Calculated column vs measure (the #1 DAX question)

| | Calculated column | Measure |
|---|---|---|
| Computed | at refresh, row by row, stored in the model | at query time, for the current filter context |
| Context | row context | filter context |
| Use for | slicing / grouping (e.g. `Age Band`), row-level attributes | aggregations shown in visuals (Revenue, AOV, YoY %) |
| Cost | uses memory | uses CPU at query time |

**Rule:** if it goes on an axis or a slicer, it's a column. If it's a number that should react to filters, it's a measure.

### Contexts and CALCULATE

* **Filter context**: the filters applied to a calculation by slicers, visual rows/columns and page filters.
* **Row context**: "the current row" inside calculated columns and iterators (`SUMX`, `AVERAGEX`, `FILTER`).
* **`CALCULATE(expr, filters…)`** evaluates `expr` in a *modified* filter context. It's the most important DAX function.
* **Context transition**: `CALCULATE` inside a row context turns the current row into filters (that's why a measure called inside `SUMX` works per row).

```DAX
Net Revenue      = CALCULATE ( SUM ( fact_sales[net_revenue] ), fact_sales[is_valid] = 1 )
AOV              = DIVIDE ( [Net Revenue], [Orders] )                  -- DIVIDE handles /0
Revenue (all categories) = CALCULATE ( [Net Revenue], ALL ( dim_product[category] ) )
Category Share   = DIVIDE ( [Net Revenue], [Revenue (all categories)] )
Revenue PY       = CALCULATE ( [Net Revenue], SAMEPERIODLASTYEAR ( dim_date[date] ) )
Revenue YoY %    = DIVIDE ( [Net Revenue] - [Revenue PY], [Revenue PY] )
Revenue FYTD     = TOTALYTD ( [Net Revenue], dim_date[date], "3/31" )  -- Indian fiscal year
Line Revenue (iterator) = SUMX ( fact_sales, fact_sales[quantity] * fact_sales[unit_price] )
Top 5 Products   = CALCULATE ( [Net Revenue], TOPN ( 5, ALL ( dim_product[product_name] ), [Net Revenue] ) )
```

`ALL` removes filters · `ALLSELECTED` keeps the outer slicer filters but ignores the visual's own grouping ·
`ALLEXCEPT(table, col)` removes all filters except those listed · `REMOVEFILTERS` = modern `ALL` as a CALCULATE modifier ·
`VALUES` / `SELECTEDVALUE` read the current filter · `USERELATIONSHIP` activates an inactive relationship (e.g. ship date vs order date).

### Other Power BI topics
* **Row-level security (RLS)**: roles with DAX filters (`[region] = "South"`), or dynamic with `USERPRINCIPALNAME()`.
* **Import vs DirectQuery vs Live connection**: Import is fastest (data cached in VertiPaq) but needs refreshes; DirectQuery queries the source live (fresh data, slower, DAX limits).
* **Performance**: star schema, remove unused columns, reduce cardinality (split datetime into date + time), measures over calculated columns, Performance Analyzer.
* **Features to mention**: drill-through, bookmarks, field parameters, tooltip pages, what-if parameters, incremental refresh, deployment pipelines.

## 3. Tableau

* **Dimensions vs measures**: qualitative vs quantitative. **Discrete (blue) vs continuous (green)**: discrete creates headers, continuous creates axes.
* **Marks card**: colour, size, label, detail and tooltip encode fields.
* **Relationships** (the logical layer, flexible, the default since 2020.2) vs **joins** (physical layer, fixed grain) vs **blending** (cross-source, aggregated at the linking fields).
* **Calculated fields**: row-level (`[Qty] * [Price]`) or aggregate (`SUM([Profit]) / SUM([Sales])`). You can't mix aggregated and unaggregated fields in one expression.
* **LOD expressions** compute at a specified level of detail, independent of the view:
  * `{FIXED [Customer Id] : MIN([Order Date])}` gives the first purchase date (cohorts!)
  * `{INCLUDE [Order Id] : SUM([Sales])}` gives order-level values, then averaged in the view (true AOV)
  * `{EXCLUDE [Region] : SUM([Sales])}` gives the total ignoring region, for % of total
* **Table calculations**: running total, percent of total, difference / percent difference, rank, moving average, computed *after* aggregation along a chosen direction (Compute Using).
* **Order of operations** (a frequent question): Extract filters → Data source filters → Context filters → **FIXED LOD** → Dimension filters → **INCLUDE/EXCLUDE LOD** → Measure filters → Table calc filters. To make a Top-N respect another filter, add that filter **to context**.
* **Parameters** (user inputs for Top N, metric switchers) · **Actions** (filter/highlight/URL) · **Sets** · **Groups** · **Hierarchies** · **Dashboard containers**.

## 4. Dashboard design principles

1. **Start from the audience's questions** ("Are we on track this quarter? Where should I act?"), not from the data.
2. **Hierarchy**: KPIs top-left → trends → breakdowns → detail. Put the most important item where the eye lands first.
3. **One insight per visual**, and state it in the title.
4. **Right chart**: line for trend, sorted bar for comparison, scatter for relationship, table for exact lookup. Avoid 3-D, dual axes that mislead, and pies with many slices.
5. **Context**: compare to the target, the prior period or the average. A number without a comparison isn't an insight.
6. **Restrained colour**: grey by default, one highlight colour for what matters, red/green only for good/bad (and colour-blind-safe).
7. **Consistent formatting**: ₹ lakh/crore or K/M, the same decimals everywhere, and show units.
8. **Performance & trust**: fast load, a "data as of" timestamp, and definitions in tooltips or an info page.

## 5. Interview questions

<details><summary><b>Measure vs calculated column?</b></summary>See the table in section 2. A column is stored per row and used for slicing; a measure is calculated at query time in filter context and used for aggregated values.</details>
<details><summary><b>What does CALCULATE do?</b></summary>It evaluates an expression under a modified filter context: adding, replacing or removing filters. Inside a row context it also performs context transition.</details>
<details><summary><b>Why use a star schema?</b></summary>Simple one-directional filter propagation, fewer joins, better compression and performance, easy for users to understand, and no ambiguous paths.</details>
<details><summary><b>How do you calculate YoY growth?</b></summary>A marked date table + <code>SAMEPERIODLASTYEAR</code> (or <code>DATEADD(-1, YEAR)</code>) for the prior-year measure, then <code>DIVIDE(current − PY, PY)</code>. In Tableau, a Percent Difference table calc or a LOOKUP-based calculation.</details>
<details><summary><b>Your dashboard is slow. What do you check?</b></summary>Model: star schema, remove unused columns and high-cardinality text, avoid bi-directional and many-to-many relationships. DAX: replace iterators over large tables and heavy calculated columns. Visuals: too many per page, high-cardinality tables. Use Performance Analyzer (Power BI) or Performance Recording (Tableau). Consider aggregations / extracts.</details>
<details><summary><b>FIXED vs INCLUDE vs EXCLUDE LOD?</b></summary>FIXED computes at exactly the listed dimensions, ignoring the view (it isn't affected by dimension filters unless they're in context). INCLUDE adds dimensions to the view's level (finer); EXCLUDE removes them (coarser).</details>
<details><summary><b>How would you implement row-level security?</b></summary>Power BI: define roles with DAX filters on dimension tables; dynamic RLS maps <code>USERPRINCIPALNAME()</code> to a user-region table; test with "View as", then assign users in the Service. Tableau: user filters or entitlement tables with <code>USERNAME()</code>.</details>
<details><summary><b>Walk me through a dashboard you built.</b></summary>Use a STAR structure: the business problem and audience → the data and model (grain, star schema) → key measures and definitions → design choices → one insight it surfaced and the action it led to. Have the ShopKart dashboard ready to screen-share.</details>
