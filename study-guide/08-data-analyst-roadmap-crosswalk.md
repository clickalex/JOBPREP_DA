# 08 · Data Analyst Roadmap crosswalk & optional extensions

This chapter checks the repository against the [roadmap.sh Data Analyst roadmap](https://roadmap.sh/data-analyst), reviewed **7 October 2026**. The roadmap is a broad learning map, not a list of requirements for every entry-level analyst job. This kit already teaches the core workflow through SQL, Excel, Python/pandas, statistics, BI, business cases, and a portfolio project. This crosswalk adds the topics that were missing or only lightly covered, and labels specialist areas as optional rather than implying you need to master them before applying.

## 1. Coverage check

| Roadmap area | Coverage in this kit before this chapter | What to use / what this chapter adds |
|---|---|---|
| Data analysis lifecycle: collect, clean, explore, analyse, visualise and communicate | **Covered** | [Python & pandas](04-python-pandas.md), [statistics](03-statistics.md), [BI](05-bi-powerbi-tableau.md), [business cases](06-business-metrics-and-case-studies.md), and the [ShopKart project](../portfolio/shopkart-growth-analysis/README.md) take a question through to recommendations. |
| SQL, databases and CSV files | **Covered** | The [SQL practice](../practice/sql/README.md) uses SQLite; the portfolio includes repeatable CSV cleaning and a star-schema dashboard. See the storage and ingestion notes below for warehouses, Parquet and APIs. |
| Excel / spreadsheet analysis | **Mostly covered** | The [Excel guide](02-excel.md) includes the roadmap's common functions, pivots, charts and cleanup. This update adds explicit HLOOKUP and basic aggregate-function coverage. Google Sheets equivalents are outlined below. |
| Descriptive statistics and visualisation | **Mostly covered** | The [statistics](03-statistics.md), [Excel](02-excel.md), and [Python charting](04-python-pandas.md) guides cover central tendency, spread, distributions, hypothesis tests and common charts. This update adds range/kurtosis cautions and a chart-selection checklist. |
| Python and data-manipulation / visualisation libraries | **Covered** | The [Python guide](04-python-pandas.md) and 25 graded exercises practise pandas, NumPy, Matplotlib and Seaborn. |
| R, dplyr and ggplot2 | **Missing** | A small optional R translation is included below. The repository's autograded path remains Python/pandas; you do not need both languages for most junior roles. |
| APIs and web scraping | **Missing** | Safe ingestion patterns, pagination, validation and responsible scraping are outlined below. No live API call is required to complete this repo's exercises. |
| Regression, supervised/unsupervised learning, common ML algorithms and evaluation | **Partial** | The [statistics guide](03-statistics.md) introduces linear and logistic regression. This chapter adds a model/algorithm map, evaluation and leakage basics, plus optional forecasting and customer-segmentation project briefs. |
| Hadoop, Spark, MapReduce, parallel processing / MPI | **Missing / specialist** | A vocabulary and “when to reach for it” overview is included below. A junior analyst should usually learn SQL and warehouse basics first; distributed-computing implementation is role-dependent. |
| Neural networks, CNNs, RNNs, TensorFlow, PyTorch, image recognition and NLP | **Missing / specialist** | Covered at orientation level below, clearly marked optional. These are usually data-science/ML specialisations, not prerequisites for a general DA role. |
| Projects, Kaggle, courses, certifications, networking | **Partly covered** | The existing [portfolio](../portfolio/shopkart-growth-analysis/README.md) and [job-search chapter](07-behavioral-and-job-search.md) cover project presentation, courses, certifications and networking. This chapter adds two further project briefs and a responsible competition workflow. |

## 2. Analytics types and the end-to-end workflow

Four useful labels describe the question being answered:

| Type | Question | Example |
|---|---|---|
| **Descriptive** | What happened? | Monthly orders, revenue and return rate |
| **Diagnostic** | Why might it have happened? | Decompose a cancellation increase by courier, region and payment method |
| **Predictive** | What is likely to happen? | Forecast next month's demand with uncertainty |
| **Prescriptive** | What action should we take? | Compare reorder options under service-level and inventory constraints |

A practical analyst workflow is: define the decision and metric → identify the right source and grain → collect authorised data → profile and clean it → explore and analyse → validate calculations → visualise and explain caveats → recommend an action → monitor the outcome. **Data mining** is a broad label for discovering useful patterns in larger datasets; it can include statistical summaries, clustering or predictive models, but it does not replace a clear question and validation. “Predictive” and “prescriptive” work is not automatically better than a clear descriptive answer; use the simplest method that supports the decision.

## 3. Data sources, APIs, spreadsheets and storage

### Ingest responsibly

* **Database:** use SQL with a read-only account when possible. Select only needed columns and use an agreed date range; do not export sensitive rows without a legitimate need and approved access.
* **CSV / spreadsheet:** record source, extraction time, encoding, delimiter, column types, timezone and row count. Preserve an untouched source copy; validate keys, missing values and totals after parsing. Don't let a spreadsheet silently convert IDs or dates.
* **API:** prefer an official API or published dataset over scraping. Check its documentation, licence and access terms. Handle authentication via an environment variable or approved secret store, not a hard-coded token or committed notebook. Respect page limits and rate limits; handle pagination, timeouts, retries/backoff, duplicate pages, schema changes and incremental updates. Save the raw response and retrieval timestamp where policy permits, then validate the parsed records.

A minimal **illustrative** Python pattern (replace the example host/path with an authorised API and follow its authentication rules):

```python
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

params = urlencode({"limit": 100, "page": 1})
request = Request(
    f"https://api.example.com/v1/events?{params}",
    headers={"Authorization": f"Bearer {os.environ['API_TOKEN']}", "Accept": "application/json"},
)
with urlopen(request, timeout=20) as response:
    payload = json.load(response)

rows = payload["data"]  # validate keys, types, count and pagination before analysis
```

This is a request example, not a working credential or guaranteed public endpoint. Production code also needs the API's pagination scheme, rate-limit handling, error logging and a secure secret configuration; never commit `.env` files or real tokens.

### Web scraping: last resort, not a bypass

Before scraping, check for an API, open-data download or permission to reuse the content. Read the site's terms and robots policy; obey rate limits, identify your client where appropriate, cache results, and collect only what is necessary. Do not bypass login, paywalls, CAPTCHAs, access controls or anti-bot measures. Avoid personal/sensitive data. If the site's rules or applicable law are unclear, ask for permission or choose another source. HTML changes, so document the extraction date and validate the output instead of treating a scraper as a stable data feed.

### Storage vocabulary

* **Relational database:** structured tables and keys; good for transactions and SQL queries. This repo's practice database is SQLite.
* **Data warehouse:** curated analytical tables, often organised around facts and dimensions; the BI guide's star schema is a useful starting point.
* **Data lake / object storage:** files such as CSV, JSON or Parquet stored cheaply; raw and curated data may coexist, so schema/catalogue and access controls matter.
* **Parquet:** compressed, columnar file format that can reduce storage and speed analytical scans compared with repeatedly parsing wide CSVs.
* **Lakehouse:** a managed approach combining lake-style storage with table metadata / transactional features. Know the idea; tool-specific internals vary.

For a single laptop-sized project, CSV + SQLite is often enough. Choose a warehouse or distributed system because scale, concurrency, governance or refresh requirements justify it—not because it sounds advanced.

## 4. Google Sheets and remaining spreadsheet functions

Most Excel skills transfer: formulas, tables, pivots, charts, sorting, filters and data validation. Google Sheets also has `QUERY` for SQL-like filtering/aggregation and `IMPORTRANGE` for importing a range from another workbook (requires access approval). Be mindful that Sheets/Excel function names, separators, array behaviour, date parsing and collaboration permissions can differ by locale and product version. Never make a public share link the default for sensitive data.

The expanded [Excel functions section](02-excel.md) now calls out `SUM`, `AVERAGE`, `COUNT`, `COUNTA`, `MIN`, `MAX`, `IF`, `DATEDIF`, HLOOKUP, VLOOKUP/XLOOKUP, and text cleanup/replacement (`TRIM`, `CLEAN`, `REPLACE`, `SUBSTITUTE`, `UPPER`, `LOWER`, `PROPER`, `CONCAT`). Check version compatibility before using newer dynamic-array functions in a timed test.

## 5. Statistics and charts: final roadmap details

* **Range** = maximum − minimum; it is easy to explain but depends only on two observations and is sensitive to outliers. Pair it with SD, IQR or percentiles.
* **Kurtosis** describes tail weight relative to a normal distribution; software may report *excess kurtosis* (normal = 0) or *Pearson kurtosis* (normal = 3). State the convention and do not use kurtosis alone to label a point an outlier.
* Central tendency in the existing statistics chapter includes mean, median and mode; spread includes variance, SD, IQR and percentiles; shape includes skew. Use plots and domain context rather than assuming one summary tells the full story.

| Need | Good starting chart | Common caution |
|---|---|---|
| Compare categories | Sorted bar | Too many categories become unreadable |
| Trend over ordered time | Line | Keep time intervals consistent; annotate important changes |
| Distribution | Histogram / box plot | Show units and consider a log scale for heavy right skew |
| Relationship between two numeric variables | Scatter | Correlation alone does not establish cause |
| Stage-by-stage conversion | Funnel | Define the cohort and whether users can skip/repeat steps |
| Part-to-whole over time | Stacked bar/area | Small segments are hard to compare; use a table or small multiples if needed |
| Matrix / intensity by two categories | Heatmap | Use a meaningful scale and label the axes |
| Simple part-to-whole with very few categories | Pie/donut, sparingly | Angles are hard to compare; sorted bars are usually clearer |

The [Excel guide](02-excel.md), [Python chart examples](04-python-pandas.md), ShopKart funnel, and dashboard cohort heatmap already give you practice with these choices.

## 6. R track: translate, don't relearn the concepts

If a role specifically asks for R, learn its data-frame workflow alongside the same analytical reasoning. Common packages are `readr` (CSV), `dplyr` (filter/group/summarise/join), `tidyr` (reshape), `ggplot2` (charts), and `lubridate` (dates). This example assumes `sales` is already a joined data frame with `month`, `category` and `net_revenue` columns:

```r
library(dplyr)
library(ggplot2)

monthly <- sales |>
  filter(!is.na(net_revenue)) |>
  group_by(month, category) |>
  summarise(revenue = sum(net_revenue), .groups = "drop")

ggplot(monthly, aes(x = month, y = revenue, colour = category)) +
  geom_line() +
  labs(title = "Monthly net revenue by category", x = NULL, y = "Net revenue")
```

Equivalent mental model: `filter` ≈ row filter, `mutate` ≈ derived columns, `group_by` + `summarise` ≈ SQL `GROUP BY`, `left_join` ≈ `LEFT JOIN`, and `ggplot` layers map data to marks. Recreate one existing SQL or pandas analysis in R only if the jobs you target ask for it; don't split practice time across tools without a reason.

## 7. Machine learning: understand the map and evaluate honestly

### Families and examples

| Family | What it learns | Roadmap examples | Analyst-level use / caution |
|---|---|---|---|
| **Supervised regression** | Numeric target from labelled examples | Linear regression; decision-tree regression | Sales/demand estimate. Compare with a simple baseline; inspect residuals and time leakage. |
| **Supervised classification** | Class or probability from labelled examples | Logistic regression, decision trees, k-nearest neighbours (KNN), Naive Bayes | Churn/fraud triage. Choose thresholds by error costs; check imbalance and calibration, not accuracy alone. |
| **Unsupervised clustering** | Groups/patterns without a target label | K-means | Customer segments for exploration. Scale numeric features, decide cluster count thoughtfully, profile clusters and test whether they are stable/actionable. A cluster is not automatically a real customer type. |
| **Reinforcement learning** | Actions learned through rewards and feedback | Agent/policy optimisation | Usually specialised; only a fit when sequential actions and reward feedback are central. Not a standard first DA technique. |

### Model evaluation checklist

1. Define the decision, target, prediction time and what an error costs. Build a simple baseline first.
2. Split data before fitting preprocessing or selecting features. Use train/validation/test or cross-validation as appropriate; for time series, use chronological/rolling splits rather than random shuffling.
3. Prevent **target leakage**: don't use information unavailable at prediction time, including post-outcome fields or aggregates that indirectly encode the answer.
4. For regression, inspect MAE (typical absolute error), RMSE (penalises large misses), residuals and a baseline; R² alone is not enough.
5. For classification, inspect the confusion matrix, precision, recall, F1 and (where useful) ROC/PR curves; choose a threshold based on the business cost of false positives/negatives. Accuracy can mislead on rare events.
6. Check performance across relevant periods and groups, communicate uncertainty and limitations, and monitor drift after release. A model score is not proof that an intervention will cause the predicted outcome.

### Two optional portfolio extensions

* **Sales trend forecast:** start with last-week/last-year seasonal baselines; plot the series, define the forecast horizon, use chronological holdouts, compare MAE with the baseline and explain the uncertainty. Include promotions/holidays only if they are available at forecast time.
* **Customer segmentation:** define a business use first; build one row per customer using a documented observation window (for example, recency, frequency and monetary value); scale features where appropriate; try K-means as an exploratory baseline; profile and validate segments for stability and actionability. Do not claim clusters prove causal differences or use sensitive attributes casually.

The existing ShopKart revenue/funnel/A/B-test project remains the core portfolio example. These extensions are options, not prerequisites.

## 8. Big data and deep learning: optional orientation

* **Scale-up vs scale-out:** use a larger machine vs distribute work across machines. Before scaling, check whether a better query, columnar storage, partition pruning, or incremental processing solves the problem.
* **Hadoop/HDFS:** distributed file storage and a broader ecosystem for cluster data processing. **MapReduce** is a batch map-then-reduce programming model. These are important concepts historically and in some legacy stacks.
* **Apache Spark:** distributed processing engine with SQL/DataFrame APIs and batch/streaming capabilities. Analysts may encounter Spark SQL or PySpark for large datasets; learn the team's existing platform rather than deploying a cluster for a small report.
* **Parallel processing / MPI:** MPI is a message-passing standard for coordinating parallel programs, common in high-performance/scientific computing. It is not normally required in a business analyst interview.
* **Deep learning:** neural networks with many learned layers. CNNs are commonly associated with image data; RNNs model sequences (modern systems may use other architectures). TensorFlow and PyTorch are popular frameworks; image recognition and NLP are application areas. These are specialist data-science topics, usually unnecessary for an entry-level analyst role.

A sensible order is SQL/Excel/Python or R → statistics and BI → reliable project work → basic model literacy → distributed or deep-learning tools only when the role and data justify them.

## 9. Practice and career extensions

1. **Forecast mini-project:** use a public, licensed dataset; create a time-based baseline and explain forecast error. Never tune on the test period.
2. **Segmentation mini-project:** document customer grain, features, scaling, method, cluster profiles, stability check and a possible action; include a “when not to use this” note.
3. **Kaggle:** choose a beginner tabular competition only after you have a baseline. Keep a local validation split, avoid leaderboard leakage, record experiments and explain the business interpretation—not only the rank. Follow the competition's data and sharing rules.
4. **Courses/certificates:** use a course to close a named gap (for example, PL-300 for a Power BI role); produce a reproducible project to demonstrate the skill. The existing [job-search guide](07-behavioral-and-job-search.md) explains why credentials alone are not evidence.
5. **Stay current and network:** follow official documentation and practitioner communities; attend a meetup/webinar or ask an analyst for an informational conversation. Verify dated tool advice before using it in an interview.

## 10. Roadmap self-check interview Q&A

<details><summary><b>Descriptive vs diagnostic vs predictive vs prescriptive analytics?</b></summary>Descriptive summarises what happened; diagnostic investigates why; predictive estimates what may happen; prescriptive compares actions. Start with the decision, not the fanciest category.</details>
<details><summary><b>What should a reliable API ingestion process handle?</b></summary>Approved access and secure credentials, pagination, rate limits, timeouts/retries, duplicate pages, schema changes and validation of types, keys, row counts and retrieval time. Preserve a raw response when policy permits.</details>
<details><summary><b>When is web scraping appropriate?</b></summary>Prefer an official API or open dataset. Scrape only when allowed by terms and applicable rules; respect robots policy and rate limits, cache data, minimise collection, and never bypass login, paywalls, CAPTCHAs or access controls.</details>
<details><summary><b>Supervised vs unsupervised learning?</b></summary>Supervised learning uses labelled examples to predict a target (regression or classification). Unsupervised learning looks for structure without a target (for example, clustering). Reinforcement learning learns actions from rewards and is a separate, usually specialised setup.</details>
<details><summary><b>Why can a high model score still be misleading?</b></summary>It may reflect leakage, an unrepresentative split, class imbalance, overfitting or a metric that doesn't match error costs. Compare to a baseline, split before preprocessing, validate on data that reflects use, and inspect relevant error metrics and groups.</details>
<details><summary><b>How should you validate a sales forecast?</b></summary>Use chronological or rolling holdouts that mimic the forecast horizon, compare against a seasonal-naive baseline, measure error (such as MAE), and report uncertainty. Never tune using the final test period.</details>
<details><summary><b>Which metrics suit regression and classification?</b></summary>For regression, MAE/RMSE plus residual checks; for classification, confusion matrix, precision, recall, F1 and possibly ROC/PR curves. Select based on business error costs; accuracy alone can fail on rare events.</details>
<details><summary><b>What does kurtosis tell you, and what does it not tell you?</b></summary>It describes tail weight relative to a normal distribution. Packages may return excess kurtosis (normal = 0) or Pearson kurtosis (normal = 3). It is not, by itself, a rule for identifying or removing outliers.</details>
<details><summary><b>When might a data analyst choose R with dplyr and ggplot2?</b></summary>When the target team, existing workflow or project uses R. dplyr handles data-frame transformations and ggplot2 builds layered charts; the same SQL, statistics and validation principles still apply. Learn one stack deeply before adding another without a role-based reason.</details>
<details><summary><b>Hadoop MapReduce vs Spark, at a high level?</b></summary>Hadoop commonly refers to a distributed storage/ecosystem; MapReduce is a batch processing model. Spark is a distributed processing engine with SQL/DataFrame APIs and batch/streaming options. Choose based on platform and scale needs; neither is needed for a small laptop-sized analysis.</details>
<details><summary><b>When would deep learning be worth exploring?</b></summary>When the problem and data justify it—for example, image recognition with CNN-style models, or text/NLP with neural methods—and simpler baselines are insufficient. TensorFlow and PyTorch are frameworks; they are optional specialisations for most entry-level analyst roles.</details>
<details><summary><b>How do you make a customer-segmentation project credible?</b></summary>Define a use case and customer/time grain, document features and scaling, test cluster stability, profile resulting groups, and show a plausible action and limitation. Clusters are exploratory groupings, not proof of causal types or automatic targeting policy.</details>

## 11. Final coverage checklist

- [ ] I can take an authorised source (database, spreadsheet, CSV or permitted API) through profiling, cleaning, analysis, validation and communication.
- [ ] I can use core Excel formulas, pivots and charts, and explain the equivalent spreadsheet workflow in Google Sheets if needed.
- [ ] I can distinguish descriptive, diagnostic, predictive and prescriptive questions; calculate and explain common statistics and select an appropriate chart.
- [ ] I can name the difference between supervised learning, unsupervised learning and reinforcement learning, and explain basic model validation/leakage.
- [ ] I know what R/dplyr/ggplot2, Spark/Hadoop and deep-learning frameworks are for, and can prioritise based on the role rather than treating every roadmap branch as mandatory.
- [ ] I have a reproducible core portfolio project; optional forecasting or segmentation work is clearly labelled and evaluated.
