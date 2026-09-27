# SQL practice: 40 graded questions

Every question runs against `data/shopkart.db` (SQLite). They go from `SELECT` basics to cohort retention, funnels,
medians without `MEDIAN()`, market-basket pairs and an anomaly hunt.

| File | Purpose |
|---|---|
| [`EXERCISES.md`](EXERCISES.md) | The questions (12 Easy · 16 Medium · 12 Hard) |
| `my_answers/qNN.sql` | **Write your answers here.** One file per question, with the prompt as a comment |
| `check.py` | Grades your answers by comparing *results* (not query text) with the reference |
| [`SOLUTIONS.md`](SOLUTIONS.md) | Reference solutions + expected output. Try first! |
| `questions.py` / `build.py` | Source of truth for the questions; `build.py` regenerates the .md files and missing starters |

```bash
python practice/sql/check.py              # grade everything you've attempted
python practice/sql/check.py 25 30        # grade specific questions
python practice/sql/check.py 25 --show    # show expected vs your output even when correct
```

**Writing queries interactively:** open `data/shopkart.db` in [DB Browser for SQLite](https://sqlitebrowser.org/),
DBeaver, or the VS Code *SQLite Viewer* extension. From Python: `pd.read_sql("SELECT ...", sqlite3.connect("data/shopkart.db"))`.

**Other dialects:** SQLite uses `strftime()` and `julianday()` for dates. The
[dialect cheat sheet](../../study-guide/01-sql.md#7-dialect-cheat-sheet) maps them to PostgreSQL, MySQL and SQL Server.
Good free places to keep practising: DataLemur, StrataScratch, LeetCode (Database), HackerRank SQL, SQLZoo.
