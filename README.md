# JOBPREP_DA: Data Analyst interview prep kit

A complete, hands-on kit for landing an **entry-level Data Analyst** role: a study guide, **85 auto-graded practice
exercises** (SQL, Python, Excel) and an **end-to-end portfolio project** with a Power BI / Tableau dashboard kit.
Everything runs on one realistic dataset, so skills build on each other.

| | What's inside | Start here |
|---|---|---|
| 📚 **Study guide** | 7 chapters: concepts, cheat sheets, pitfalls, interview Q&A | [`study-guide/`](study-guide/) |
| 🗄️ **SQL practice** | 40 questions, Easy → Hard, auto-graded | [`practice/sql/`](practice/sql/) |
| 🐍 **Python practice** | 25 pandas/stats exercises, auto-graded | [`practice/python/`](practice/python/) |
| 📊 **Excel practice** | 20-task workbook that grades itself | [`practice/excel/`](practice/excel/) |
| 💼 **Portfolio project** | Cleaning → analysis → A/B test → recommendations → dashboard | [`portfolio/shopkart-growth-analysis/`](portfolio/shopkart-growth-analysis/) |
| 🧾 **Dataset** | ShopKart, a fictional Indian e-commerce company (8k customers, 12k orders, clickstream, A/B test) | [`data/`](data/) |

---

## Quick start

```bash
git clone <this repo> && cd JOBPREP_DA
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python practice/sql/check.py        # 0 passed · 40 not attempted — let's change that
python practice/python/check.py
```

The data files are committed, so you can start straight away. `python data/generate_data.py` rebuilds them identically.
No Python yet? You can still use the Excel workbook, the SQLite database (open it in *DB Browser for SQLite*) and the
dashboard CSVs in Power BI / Tableau.

## The study guide

| # | Chapter | Covers |
|---|---|---|
| 01 | [SQL](study-guide/01-sql.md) | execution order, joins & fan-out, NULLs, CTEs, **window functions**, patterns (top-N, dedupe, cohorts, median), dialect cheat sheet |
| 02 | [Excel](study-guide/02-excel.md) | XLOOKUP/INDEX-MATCH, SUMIFS, dynamic arrays, PivotTables, Power Query, data-cleaning tricks |
| 03 | [Statistics & A/B testing](study-guide/03-statistics.md) | distributions, CLT, CIs, p-values, test selection, **sample size**, A/B pitfalls, worked example |
| 04 | [Python & pandas](study-guide/04-python-pandas.md) | SQL→pandas table, cleaning recipes, groupby/merge/pivot, time series, gotchas |
| 05 | [Power BI & Tableau](study-guide/05-bi-powerbi-tableau.md) | star schema, **DAX & CALCULATE**, time intelligence, LODs, order of operations, design principles |
| 06 | [Business metrics & cases](study-guide/06-business-metrics-and-case-studies.md) | e-commerce/SaaS metrics, metric trees, "metric dropped" framework, guesstimates |
| 07 | [Behavioral & job search](study-guide/07-behavioral-and-job-search.md) | hiring process, STAR stories, resume/ATS, portfolio, India job-search notes |

## An 8-week plan (≈ 10–12 hours/week)

| Week | Learn | Do | Done when |
|---|---|---|---|
| 1 | SQL §1–4 | SQL Q1–12 | All Easy questions pass |
| 2 | SQL §5–6 (window functions) | SQL Q13–28 | Medium questions pass, ~10 min each |
| 3 | Excel guide | Excel workbook tasks 1–20 + bonus dashboard | Score 20/20 without the answer key |
| 4 | Python/pandas guide | Python p01–p18 | Cleaning + analysis sections pass |
| 5 | Statistics guide | Python p19–p25, SQL Q29–40 | You can explain the A/B readout out loud |
| 6 | BI guide | Build the ShopKart dashboard (3 pages) | Your KPIs match the target numbers; published or screenshotted |
| 7 | Metrics & cases guide | Re-do the portfolio analysis **your own way** + add one new question | README in your own words, on your GitHub |
| 8 | Behavioral guide | 6 STAR stories, resume, LinkedIn, 3 mock interviews | Applying daily; referrals requested |

Already comfortable with a topic? Run the checker on the Hard questions first, and skip ahead if they pass.

## What the data hides (and which exercises find it)

| Pattern | Where you'll find it |
|---|---|
| Growth +89% YoY and a Diwali spike | SQL Q25/Q31/Q38 · Python p08/p16 · Portfolio §2 |
| Electronics = revenue, Fashion = profit (but 16% returns) | SQL Q13/Q17/Q19 · Portfolio §3 |
| Referral customers are worth ~2.4x Paid Social ones | Python p25 · Portfolio §4 |
| Cash on Delivery cancels ~3x more | SQL Q18 · Excel task 5 · Portfolio §5 |
| A courier outage in one state, one month | SQL Q34 · Portfolio §5 |
| Mobile Web funnel leaks | SQL Q28 · Python p18 |
| Checkout A/B test: wins overall, but only on the App | SQL Q35 · Python p19–p20 · Stats guide · Portfolio §6 |
| Messy raw exports | Python p01–p06 · Portfolio §1 |

## Repo map

```
JOBPREP_DA/
├── data/
│   ├── generate_data.py         # deterministic generator (seed 42)
│   ├── schema.sql · README.md   # schema + data dictionary + metric definitions
│   ├── shopkart.db              # SQLite database (SQL practice)
│   ├── clean/*.csv              # analysis-ready tables
│   └── raw/*.csv                # messy exports (cleaning practice)
├── study-guide/                 # 7 chapters
├── practice/
│   ├── sql/                     # EXERCISES.md · my_answers/ · check.py · SOLUTIONS.md
│   ├── python/                  # exercises.py · check.py · solutions.py · data_loader.py
│   └── excel/                   # ShopKart_Excel_Practice.xlsx · build_workbook.py
└── portfolio/shopkart-growth-analysis/
    ├── README.md                # the case-study write-up
    ├── analysis.ipynb           # executed notebook
    ├── build_notebook.py        # regenerates notebook + figures
    ├── src/cleaning.py          # logged cleaning pipeline
    ├── figures/                 # charts
    └── dashboard/               # star-schema CSVs, DAX, Tableau calcs, build guide, preview
```

## Notes

* **The data is synthetic.** It's built to behave like real e-commerce data with realistic problems, and it's reproducible so the auto-graders work. For your public portfolio, **personalise the project** (see its *Make it yours* section) or repeat the workflow on a real public dataset.
* Commit your practice answers to your own fork. A history of solved problems is a nice signal in itself.
