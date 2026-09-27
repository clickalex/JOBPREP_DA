# Excel practice workbook

**[`ShopKart_Excel_Practice.xlsx`](ShopKart_Excel_Practice.xlsx)**: 4,541 order lines (Oct–Dec 2025) and 20 tasks.

1. Open the workbook and read **Start Here**.
2. Work on the **Orders** sheet (an Excel Table, `tblOrders`), adding helper columns as the tasks suggest.
3. Type answers in the yellow cells on **Tasks**. The Result column shows ✅ / ❌ and there's a score at the bottom.
4. Stuck? **Answer Key** has one working formula per task.

Skills: XLOOKUP · VLOOKUP · INDEX/MATCH · SUMIFS (incl. OR logic) · COUNTIFS · AVERAGEIFS · MAXIFS · IF · TEXT/DATE ·
WEEKDAY · SUMPRODUCT · distinct counts (with and without conditions) · LARGE · PivotTables · % of total. Bonus tasks
cover Power Query, conditional formatting and building a one-page dashboard.

> Works in Excel 2019 / 2021 / 365 (MAXIFS needs 2019+; XLOOKUP hints need 2021/365, but INDEX/MATCH alternatives are given).
> Google Sheets and LibreOffice open it too, though a few functions differ.

Rebuild the workbook (e.g. after regenerating the data): `python practice/excel/build_workbook.py`.
Every Answer Key formula was verified against pandas with the `formulas` calculation engine.
