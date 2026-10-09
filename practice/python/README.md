# Python / pandas practice: 28 graded exercises

| Section | Exercises | Skills |
|---|---|---|
| A. Cleaning (raw files) | p01–p06 | duplicates, string standardisation, mixed date formats, type fixes, outliers, imputation |
| B. Analysis | p07–p18 | merge, groupby/agg, pivot_table, value_counts, cumcount, resample, rolling, pct_change, cohort matrix, funnel |
| C. Statistics | p19–p22 | two-proportion z-test + CI, segment analysis, IQR outliers, Welch t-test |
| D. Putting it together | p23–p25 | market-basket pairs, hierarchy traversal, channel LTV |
| E. API ingestion | p26–p28 | flatten paginated JSON, de-duplication, type coercion, ingestion validation report (cached fixture, no network) |

```bash
# write your code in exercises.py (replace each `raise NotImplementedError`), then:
python practice/python/check.py            # grade everything attempted
python practice/python/check.py 4 17       # specific exercises
python practice/python/check.py 4 --show   # print expected vs yours
```

* `data_loader.py`: `load_clean()` / `load_raw()` / `load_api_pages()` helpers you can also use in your own notebooks.
* `solutions.py`: reference answers (there are many valid approaches; the checker compares results).
* Prefer notebooks? `from exercises import *` in Jupyter, experiment, then paste the final code back into `exercises.py`.
