# JOBPREP_DA: Data Analyst interview prep kit

[![CI](https://github.com/clickalex/JOBPREP_DA/actions/workflows/ci.yml/badge.svg)](https://github.com/clickalex/JOBPREP_DA/actions/workflows/ci.yml)
[![Website](https://github.com/clickalex/JOBPREP_DA/actions/workflows/pages.yml/badge.svg)](https://clickalex.github.io/JOBPREP_DA/)
[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-24292f?logo=github)](https://codespaces.new/clickalex/JOBPREP_DA)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/clickalex/JOBPREP_DA/main?labpath=portfolio%2Fshopkart-growth-analysis%2Fanalysis.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A complete, hands-on kit for landing an **entry-level Data Analyst** role: a study guide, **85 auto-graded practice
exercises** (SQL, Python, Excel), **mock interviews**, and an **end-to-end portfolio project** with a Power BI / Tableau
dashboard kit. Everything runs on one realistic dataset, so skills build on each other.

> **🌐 Website:** **[clickalex.github.io/JOBPREP_DA](https://clickalex.github.io/JOBPREP_DA/)** has the whole kit as a
> searchable site, plus an **[in-browser SQL Playground](https://clickalex.github.io/JOBPREP_DA/playground/)** (all 40
> questions, graded instantly, nothing to install) and **[flashcards](https://clickalex.github.io/JOBPREP_DA/flashcards/)**.

| | What's inside | Start here |
|---|---|---|
| 📚 **Study guide** | 7 chapters: concepts, cheat sheets, pitfalls, interview Q&A | [`study-guide/`](study-guide/) |
| 🗄️ **SQL practice** | 40 questions, Easy → Hard, auto-graded, locally or [in the browser](https://clickalex.github.io/JOBPREP_DA/playground/) | [`practice/sql/`](practice/sql/) |
| 🐍 **Python practice** | 25 pandas/stats exercises, auto-graded | [`practice/python/`](practice/python/) |
| 📊 **Excel practice** | 20-task workbook that grades itself | [`practice/excel/`](practice/excel/) |
| 🎤 **Mock interviews** | Live SQL round (also as a [timed, auto-graded mock](https://clickalex.github.io/JOBPREP_DA/playground/#m1)), case round, take-home, stats rapid-fire, all with scripts and rubrics | [`mock-interviews/`](mock-interviews/) |
| 🃏 **Flashcards** | 54 interview Q&As from the study guide (web + Anki import) | [`study-guide/flashcards.csv`](study-guide/flashcards.csv) |
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
python progress.py                  # one-screen progress report + what to do next
```

**No setup at all?** Use the [SQL Playground](https://clickalex.github.io/JOBPREP_DA/playground/) in your browser, or
click **Open in Codespaces** above for a ready-made VS Code environment in the cloud (Python, Jupyter and SQLite viewer
preinstalled).

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
| 8 | Behavioral guide | 6 STAR stories, resume, LinkedIn, the 4 [mock interviews](mock-interviews/) | Applying daily; referrals requested |

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
├── mock-interviews/             # interviewer scripts + rubrics (SQL, case, take-home, stats)
├── portfolio/shopkart-growth-analysis/
│   ├── README.md                # the case-study write-up
│   ├── analysis.ipynb           # executed notebook
│   ├── build_notebook.py        # regenerates notebook + figures
│   ├── src/cleaning.py          # logged cleaning pipeline
│   ├── figures/                 # charts
│   └── dashboard/               # star-schema CSVs, DAX, Tableau calcs, build guide, preview
├── progress.py                  # combined SQL + pandas progress report
├── website/                     # GitHub Pages site: build_site.py, mkdocs.yml, SQL playground (sql.js)
├── tests/                       # pytest suite + headless playground test (run by CI)
├── ci/workflows/                # ci.yml (tests on Linux/Windows/macOS) · pages.yml (deploys the site); see ci/README.md
└── .devcontainer/               # one-click GitHub Codespaces environment
```

## Deploy your own copy on GitHub

Fork the repo, then you get the same website and CI for free:

0. **One-time:** move `ci/workflows/` to `.github/workflows/` (steps in [`ci/README.md`](ci/README.md)).
1. **Settings ▸ Pages ▸ Build and deployment ▸ Source: _GitHub Actions_.**
2. Push to `main` (or run **Actions ▸ Deploy site to GitHub Pages ▸ Run workflow**). Your site appears at
   `https://<your-username>.github.io/JOBPREP_DA/`. URLs are picked up from the repository automatically.
3. Commit your answers in `practice/sql/my_answers/` and `practice/python/exercises.py` as you go. A history of solved
   problems is a nice signal in itself.

Preview the site locally:

```bash
pip install -r requirements.txt -r website/requirements.txt
python website/build_site.py && mkdocs serve -f website/mkdocs.yml     # http://127.0.0.1:8000
```

## Tests & CI

Once the workflows are activated ([`ci/README.md`](ci/README.md)), every push and pull request runs the test suite on **Linux, Windows and macOS** (Python 3.10–3.13):

* the dataset matches its checksums and regenerates byte-for-byte;
* all 40 SQL and 25 pandas reference solutions pass their graders, and the graders reject wrong answers
  (wrong values, wrong row order, wrong column count);
* the browser playground's grader passes all 40 solutions inside **sql.js** (Node, headless);
* every Excel Answer Key formula is evaluated by a formula engine and matches the expected answer;
* the portfolio notebook executes top to bottom;
* every relative link and `#anchor` in the markdown resolves, and the website builds with `--strict`.

```bash
pip install -r requirements-dev.txt
pytest            # fast suite (~20 s)
pytest -m slow    # Excel formula evaluation + notebook execution (~2 min)
```

## Notes

* **The data is synthetic.** It's built to behave like real e-commerce data with realistic problems, and it's reproducible so the auto-graders work. For your public portfolio, **personalise the project** (see its *Make it yours* section) or repeat the workflow on a real public dataset.
* Code is [MIT-licensed](LICENSE). The bundled [sql.js](https://github.com/sql-js/sql.js) is MIT-licensed too.
