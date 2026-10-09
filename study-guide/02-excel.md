# 02 · Excel for data analyst interviews

Excel still shows up in most entry-level DA interviews, especially in India's services, consulting, e-commerce
ops and MIS roles. Expect a **timed practical test** (clean a sheet, build a pivot, answer 5–10 questions in 30–45
minutes) plus a few "how would you…" questions.

**Practice:** [`practice/excel/ShopKart_Excel_Practice.xlsx`](../practice/excel/) has 20 tasks on 4,500 order lines.
Answers grade themselves inside Excel.

---

## 1. Functions you must know cold

**Core arithmetic and logic:** `SUM`, `AVERAGE`, `COUNT` (numbers only), `COUNTA` (non-empty), `MIN`, `MAX`, and `IF`.
For text cleaning, `REPLACE(text, start, count, new_text)` changes characters by position; `SUBSTITUTE(text, old, new)` replaces matching text. Both exist alongside `TRIM`, `CLEAN`, `PROPER`, `UPPER` and `LOWER` below.

### Lookups
| Function | Syntax | Notes |
|---|---|---|
| **XLOOKUP** (365/2021) | `=XLOOKUP(lookup, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])` | Exact match by default, can look left, returns whole rows/columns. **Use this if available** |
| VLOOKUP | `=VLOOKUP(lookup, table, col_index, FALSE)` | Always pass `FALSE` (exact). Can't look left, and breaks if columns are inserted |
| HLOOKUP | `=HLOOKUP(lookup, table, row_index, FALSE)` | Horizontal lookup; same exact-match caution as VLOOKUP. Prefer XLOOKUP or INDEX/MATCH for new work |
| INDEX/MATCH | `=INDEX(return_col, MATCH(lookup, lookup_col, 0))` | Works in every version and can look left: the classic interview answer |
| 2-way lookup | `=INDEX(grid, MATCH(row_key, row_hdrs, 0), MATCH(col_key, col_hdrs, 0))` | Or nested XLOOKUP |
| Multiple criteria | `=XLOOKUP(1, (A:A=x)*(B:B=y), C:C)` | Or a helper "key" column `=A2&"|"&B2` |

### Conditional aggregation
`SUMIFS(sum_range, crit_range1, crit1, …)`, `COUNTIFS`, `AVERAGEIFS`, `MAXIFS`, `MINIFS`

* Criteria are strings: `">=3000"`, `"<>Cancelled"`, `"*phone*"` (wildcards), `">="&DATE(2025,11,1)`, `">"&F1`.
* **OR logic** isn't built in: add two SUMIFS, or `=SUM(SUMIFS(rev, status, {"Delivered","Shipped"}))`.
* `SUMPRODUCT` handles anything: `=SUMPRODUCT((region="South")*(category="Beauty")*revenue)`.

### Logic & text
`IF`, `IFS`, `IFERROR`, `AND`/`OR`, `SWITCH` · `TRIM`, `CLEAN`, `PROPER`/`UPPER`/`LOWER`, `LEFT`/`RIGHT`/`MID`,
`LEN`, `FIND`/`SEARCH`, `SUBSTITUTE`, `TEXT`, `VALUE`, `TEXTJOIN`, `TEXTSPLIT` (365), `CONCAT` / `&`

### Dates
`TODAY`, `DATE(y,m,d)`, `YEAR`/`MONTH`/`DAY`, `EOMONTH(d, 0)` (month end), `EDATE(d, n)` (add months), `WEEKDAY(d, 2)`
(Mon = 1), `WEEKNUM`, `NETWORKDAYS`, `DATEDIF(start, end, "m")`, `TEXT(d, "yyyy-mm")` / `TEXT(d, "mmm")`.
Remember that dates are just numbers (days since 1900), so subtracting two dates gives the days between them.

### Dynamic arrays (Excel 365, a big plus in interviews)
`UNIQUE`, `FILTER`, `SORT`, `SORTBY`, `SEQUENCE`, `XMATCH`, `LET`, `LAMBDA`, `TAKE`/`DROP`, `VSTACK`/`HSTACK`, `GROUPBY`/`PIVOTBY` (newest builds)

```excel
=COUNTA(UNIQUE(tblOrders[order_id]))                              distinct count
=FILTER(tblOrders, (tblOrders[status]="Cancelled")*(tblOrders[region]="West"))
=SORTBY(UNIQUE(tblOrders[city]), SUMIFS(tblOrders[rev], tblOrders[city], UNIQUE(tblOrders[city])), -1)
=LET(r, tblOrders[rev], v, tblOrders[status]="Delivered", SUM(r*v)/SUM(--v))
```

### Distinct counts without 365
`=SUMPRODUCT(1/COUNTIF(A2:A500, A2:A500))`. With a condition:
`=SUMPRODUCT((cond_range="X")/COUNTIFS(key_range, key_range, cond_range, cond_range))`.
Or use a PivotTable with *Add this data to the Data Model* ▸ **Distinct Count**.

## 2. PivotTables

* Source data should be a **Table** (Ctrl + T): no blank rows or merged cells, one header row.
* Rows / Columns / Values / Filters; **Value Field Settings ▸ Show Values As** gives % of Grand Total, % of Row, Running Total, Difference From (MoM), Rank.
* **Group** dates by Months/Quarters/Years; group numbers into bins.
* **Slicers** and **Timelines** for interactivity; *Report Connections* links one slicer to several pivots.
* **Calculated Field** (e.g. `=Revenue/Orders`), but note that it sums first, then divides, which is what you want for ratios.
* `GETPIVOTDATA` references pivot cells robustly; *Refresh All* (Ctrl + Alt + F5) after data changes.
* Data Model / Power Pivot: relate several tables and write DAX measures (see the [BI guide](05-bi-powerbi-tableau.md)).

## 3. Power Query (Get & Transform)

This is the "ETL inside Excel", and a strong differentiator for freshers. Data ▸ Get Data ▸ From File / Folder / Web.

* Every step is recorded and **repeatable**: next month you just hit *Refresh*.
* Common steps: promote headers, change types, trim/clean, split column, replace values, remove duplicates, fill down, **unpivot** (wide → long), merge queries (= joins), append queries (= UNION), group by, conditional column.
* Try it: load `data/raw/orders_raw.csv` and standardise `status` (Trim ▸ Capitalize Each Word) and `payment_method` (Replace Values / a mapping table + Merge).

## 4. Charts & dashboards

* Pick the chart for the question: **trend** → line; **compare categories** → sorted bar; **composition** → stacked bar (avoid pies with more than 3 slices); **relationship** → scatter; **distribution** → histogram / box plot.
* Title = the insight ("COD cancels 3x more than UPI"), not the chart type.
* Dashboard sheet: KPI cards (linked cells with big fonts), 2–4 charts from pivots, slicers, no gridlines, consistent colours.
* Conditional formatting: data bars, colour scales, and formula rules like `=$I2="Cancelled"` to highlight a whole row.

## 5. Data hygiene tricks they test

| Problem | Fix |
|---|---|
| Numbers stored as text (green triangles) | `VALUE()`, `--A2`, Text to Columns ▸ Finish, or Paste Special ▸ Multiply by 1 |
| Extra spaces / non-printing characters | `TRIM(CLEAN(A2))`, `SUBSTITUTE(A2, CHAR(160), " ")` |
| Duplicates | Data ▸ Remove Duplicates (on a copy!), or `COUNTIFS(...)>1` to flag them |
| Dates as text / mixed formats | `DATEVALUE`, Text to Columns with the right date order (DMY!), Power Query locale |
| Blank cells to fill down | Select ▸ Go To Special ▸ Blanks ▸ `=` ↑ ▸ Ctrl + Enter |
| Inconsistent categories | Data Validation dropdown lists to *prevent* them; a mapping table + XLOOKUP to *fix* them |

## 6. Shortcuts that make you look fluent

`Ctrl + T` table · `Ctrl + Shift + L` filter · `Ctrl + Arrow` jump to edge · `Ctrl + Shift + Arrow` select to edge ·
`Ctrl + D` fill down · `Ctrl + ;` today's date · `F4` toggle `$` absolute refs · `Alt + =` AutoSum ·
`Ctrl + 1` format cells · `Alt + N + V` pivot · `Ctrl + [` go to precedents · `F9` evaluate part of a formula

## 7. Interview questions

<details><summary><b>VLOOKUP vs XLOOKUP vs INDEX/MATCH?</b></summary>VLOOKUP needs the key in the first column, uses a fragile column number and defaults to approximate match. INDEX/MATCH looks in any direction and survives column inserts. XLOOKUP combines both with simpler syntax, an if_not_found argument and exact match by default (Excel 2021/365 only).</details>
<details><summary><b>Relative vs absolute references?</b></summary><code>A1</code> shifts when copied; <code>$A$1</code> is fixed; <code>$A1</code> / <code>A$1</code> are mixed (lock the column / row). F4 cycles through them.</details>
<details><summary><b>How would you compare two lists to find missing items?</b></summary><code>=ISNA(MATCH(A2, OtherList, 0))</code> or <code>=COUNTIF(OtherList, A2)=0</code>, or XLOOKUP with an if_not_found value; in Power Query, a Left Anti merge.</details>
<details><summary><b>How do you handle a 1-million-row file?</b></summary>Don't open it in the grid: load it via Power Query into the Data Model and summarise with a PivotTable / DAX, or move to SQL / Python. The Excel grid tops out at 1,048,576 rows.</details>
<details><summary><b>What's the difference between a formula and a function?</b></summary>A formula is any expression starting with =; a function is a named built-in operation used inside formulas (SUM, XLOOKUP…).</details>
<details><summary><b>How do you avoid #N/A / #DIV/0! showing up?</b></summary>Wrap with <code>IFERROR(x, "")</code> or <code>IFNA</code>, but understand <i>why</i> the error occurred first; don't hide real data problems.</details>
<details><summary><b>What's a what-if analysis tool you've used?</b></summary>Goal Seek (find the input that hits a target), Data Tables (sensitivity grid), Scenario Manager, Solver (optimisation).</details>
