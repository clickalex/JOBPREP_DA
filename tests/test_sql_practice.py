"""SQL practice: every reference solution passes the grader, and the grader rejects wrong answers."""
import re

import pytest

from conftest import ROOT, load_module

SQL = ROOT / "practice" / "sql"
check = load_module("sql_check", SQL / "check.py")
QUESTIONS = check.QUESTIONS
BY_ID = {q["id"]: q for q in QUESTIONS}


@pytest.fixture
def answers(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "ANSWERS", tmp_path)
    return tmp_path


def write(folder, qid, sql):
    (folder / f"q{qid:02d}.sql").write_text(f"-- test\n{sql}\n", encoding="utf-8")


def test_question_bank_shape():
    assert [q["id"] for q in QUESTIONS] == list(range(1, 41))
    assert {q["level"] for q in QUESTIONS} == {"Easy", "Medium", "Hard"}
    for q in QUESTIONS:
        assert q["title"] and q["prompt"] and q["solution"].strip()


def test_all_reference_solutions_pass(answers, capsys):
    for q in QUESTIONS:
        write(answers, q["id"], q["solution"])
    assert check.main([]) == 0
    assert "40 passed" in capsys.readouterr().out


def test_empty_starters_count_as_not_attempted(capsys):
    """The committed my_answers/ starters must be blank templates, not solutions."""
    assert len(list((SQL / "my_answers").glob("q*.sql"))) == 40
    assert check.main([]) == 0
    assert "40 not attempted" in capsys.readouterr().out


def test_wrong_value_is_rejected(answers, capsys):
    write(answers, 9, BY_ID[9]["solution"].replace("SUM(", "1.01 * SUM(", 1))
    assert check.main(["9"]) == 1
    assert "values differ" in capsys.readouterr().out


def test_wrong_order_is_rejected(answers, capsys):
    q = next(q for q in QUESTIONS if q["ordered"] and re.search(r"ORDER BY .+ DESC\s*;?\s*$", q["solution"], re.S))
    flipped = re.sub(r"DESC(\s*;?\s*)$", r"ASC\1", q["solution"].rstrip())
    write(answers, q["id"], flipped)
    assert check.main([str(q["id"])]) == 1
    assert "wrong ORDER" in capsys.readouterr().out


def test_wrong_column_count_and_sql_errors(answers, capsys):
    write(answers, 2, "SELECT 1, 2, 3;")
    write(answers, 3, "SELEC broken")
    assert check.main(["2", "3"]) == 1
    out = capsys.readouterr().out
    assert "columns" in out and "SQL error" in out


def test_generated_markdown_is_in_sync():
    ex = (SQL / "EXERCISES.md").read_text(encoding="utf-8")
    sol = (SQL / "SOLUTIONS.md").read_text(encoding="utf-8")
    for q in QUESTIONS:
        assert q["title"] in ex and q["title"] in sol, f"Q{q['id']}: run python practice/sql/build.py"
        assert q["solution"].strip().splitlines()[0] in sol
