"""
Build the GitHub Pages site (MkDocs Material) from the repository's markdown.

    python website/build_site.py            # stage docs + generated assets into website/_build_docs
    mkdocs serve -f website/mkdocs.yml      # preview at http://127.0.0.1:8000
    mkdocs build -f website/mkdocs.yml --strict   # what CI runs (fails on broken links)

The repo stays the single source of truth: markdown is copied (not moved) into a
staging folder, and links are rewritten so they work on the website:
  * links to folders       -> that folder's README page
  * links to notebooks     -> the rendered HTML copy
  * links to files that aren't published (code, CSVs, …) -> the file on GitHub
It also generates the SQL playground data (questions + expected results) and the
flashcards (from the <details> Q&As in the study guide).
"""
from __future__ import annotations

import csv
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STAGE = HERE / "_build_docs"
sys.path.insert(0, str(ROOT / "practice" / "sql"))
from questions import QUESTIONS  # noqa: E402

PAGES = [  # markdown published on the site (paths relative to the repo root)
    "README.md",
    "study-guide/*.md",
    "practice/sql/README.md", "practice/sql/EXERCISES.md", "practice/sql/SOLUTIONS.md",
    "practice/python/README.md", "practice/excel/README.md",
    "mock-interviews/*.md",
    "portfolio/shopkart-growth-analysis/README.md",
    "portfolio/shopkart-growth-analysis/dashboard/README.md",
    "data/README.md",
]
STATIC = [  # non-markdown files published as-is
    "portfolio/shopkart-growth-analysis/figures/*.png",
    "portfolio/shopkart-growth-analysis/dashboard/dashboard_preview.png",
    "practice/excel/ShopKart_Excel_Practice.xlsx",
    "study-guide/flashcards.csv",
]
LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")      # any ](target), incl. badges nested in links
HREF_RE = re.compile(r'(href=")([^"]+)(")')
QA_RE = re.compile(r"<details><summary>(.*?)</summary>(.*?)</details>", re.S)


def repo_slug() -> str:
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout
        m = re.search(r"github\.com[:/](.+?/.+?)(?:\.git)?$", url.strip())
        if m:
            return m.group(1)
    except OSError:
        pass
    return "clickalex/JOBPREP_DA"


GITHUB = f"https://github.com/{repo_slug()}"
BRANCH = "main"


# --------------------------------------------------------------------------- staging
def expand(patterns):
    for pat in patterns:
        yield from sorted(ROOT.glob(pat))


def stage_files():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for src in list(expand(PAGES)) + list(expand(STATIC)):
        dst = STAGE / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copytree(HERE / "assets", STAGE / "assets")


def render_notebook():
    from nbconvert import HTMLExporter
    import nbformat
    nb_path = ROOT / "portfolio/shopkart-growth-analysis/analysis.ipynb"
    body, _ = HTMLExporter(template_name="lab").from_notebook_node(nbformat.read(nb_path, as_version=4))
    out = STAGE / nb_path.relative_to(ROOT).with_suffix(".html")
    out.write_text(body, encoding="utf-8")


# --------------------------------------------------------------------------- generated content
def build_playground():
    import markdown
    con = sqlite3.connect(ROOT / "data" / "shopkart.db")
    out = []
    for q in QUESTIONS:
        cur = con.execute(q["solution"])
        out.append({
            "id": q["id"], "level": q["level"], "topics": q["topics"], "title": q["title"],
            "prompt_html": markdown.markdown(q["prompt"], extensions=["sane_lists"]),
            "ordered": q["ordered"], "solution": q["solution"].strip(),
            "expected": {"columns": [d[0] for d in cur.description], "rows": [list(r) for r in cur.fetchall()]},
        })
    dst = STAGE / "playground"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "questions.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    mock = extract_mock_questions()
    for q in mock:
        cur = con.execute(q["solution"])
        q["expected"] = {"columns": [d[0] for d in cur.description], "rows": [list(r) for r in cur.fetchall()]}
    (dst / "mock.json").write_text(json.dumps(mock, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copy2(ROOT / "data" / "shopkart.db", dst / "shopkart.db")
    shutil.copy2(HERE / "pages" / "playground.md", dst / "index.md")
    return len(out)


# Live SQL rounds used by the playground's timed mock mode, in order. Question ids are global (m1, m2, …) so
# round 1 keeps its original #m1…#m7 links; append new rounds at the end so existing ids never change.
MOCK_ROUNDS = [
    (1, "Round 1 · Core SQL", ROOT / "mock-interviews" / "01-live-sql-round.md"),
    (2, "Round 2 · Product & marketing", ROOT / "mock-interviews" / "05-live-sql-round-2.md"),
    (3, "Round 3 · Advanced SQL", ROOT / "mock-interviews" / "06-live-sql-round-3.md"),
]


def extract_mock_questions(rounds=None) -> list[dict]:
    """Turn the live-SQL-round interviewer scripts into playground questions (single source of truth: the markdown)."""
    out = []
    for rnd, name, path in (rounds or MOCK_ROUNDS):
        for q in _extract_round(path):
            q.update(id=f"m{len(out) + 1}", round=rnd, round_name=name,
                     topics=f"Live SQL round {rnd} · ≈{q['minutes']} min")
            out.append(q)
    return out


def _extract_round(path: Path) -> list[dict]:
    import markdown

    def md(t):
        return markdown.markdown(t.strip())

    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^## (?=Q\d+ · )", text, flags=re.M)[1:]
    out = []
    for sec in sections:
        sec = sec.split("\n---", 1)[0]
        head = re.match(r"Q(\d+) · (.+?)\s*\((?:stretch, )?≈(\d+) min\)", sec)
        num, title, minutes = int(head.group(1)), head.group(2).strip(), int(head.group(3))
        quote = " ".join(ln[2:].strip() for ln in sec.splitlines() if ln.startswith("> "))
        bullets = re.findall(r"^- \*\*(Hint[^:]*|Follow-up[^:]*):\*\* (.+?)(?=^- \*\*|^\s*$)", sec, flags=re.M | re.S)
        hints, followups = [], []
        for label, body in bullets:
            body = " ".join(body.split())
            if label.startswith("Hint"):
                hints.append(md(body.strip('"')))
            else:
                m = re.match(r'^"(.+?)"\s*(?:\((.*)\))?$', body, flags=re.S)
                q_part, a_part = (m.group(1), m.group(2) or "") if m else (body, "")
                followups.append({"question": md(q_part), "answer": md(a_part) if a_part else ""})
        looking = re.search(r"^\*\*Looking for:\*\* (.+?)(?=^\s*$)", sec, flags=re.M | re.S)
        if looking:
            hints.append("<p><b>What the interviewer is looking for:</b></p>" + md(" ".join(looking.group(1).split())))
        answer = sec.split("<summary>Answer key</summary>", 1)[1]
        solution = re.search(r"```sql\n(.+?)```", answer, flags=re.S).group(1).strip()
        out.append({"num": num, "level": "Mock", "title": title, "minutes": minutes,
                    "prompt_html": md(quote.strip('"')),
                    "hints": hints, "followups": followups, "ordered": False, "solution": solution})
    return out


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def extract_flashcards() -> list[dict]:
    cards = []
    for md in sorted((ROOT / "study-guide").glob("*.md")):
        text = md.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        chapter = re.sub(r"^\d+\s*·\s*", "", title).split(" for ")[0].strip()
        for n, (q, a) in enumerate(QA_RE.findall(text), start=1):
            a = re.sub(r'<a href="[^"]*">(.*?)</a>', r"\1", a.strip())   # links don't work on a card
            cards.append({"id": f"{md.stem}-{n}", "chapter": chapter, "question": strip_tags(q), "answer_html": a})
    return cards


def write_flashcards(cards, csv_path: Path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        f.write("#separator:Semicolon\n#html:true\n#columns:Front;Back;Tags\n")
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        for c in cards:
            w.writerow([html.escape(c["question"]), c["answer_html"], "jobprep_da " + c["chapter"].lower().replace(" ", "_").replace("&", "and")])


def build_flashcards():
    cards = extract_flashcards()
    write_flashcards(cards, ROOT / "study-guide" / "flashcards.csv")      # committed copy (Anki users on GitHub)
    dst = STAGE / "flashcards"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "flashcards.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(ROOT / "study-guide" / "flashcards.csv", dst / "flashcards.csv")
    shutil.copy2(HERE / "pages" / "flashcards.md", dst / "index.md")
    return len(cards)


# --------------------------------------------------------------------------- link rewriting
def rewrite_target(target: str, src_rel: Path) -> str:
    if re.match(r"^[a-z]+:", target) or target.startswith(("#", "/", "<")):
        return target
    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    if not path:
        return target
    repo_target = (ROOT / src_rel.parent / path).resolve()
    try:
        rel_to_root = repo_target.relative_to(ROOT)
    except ValueError:
        return target
    staged = STAGE / rel_to_root
    if repo_target.is_dir():
        pages = sorted(staged.glob("*.md"), key=lambda f: (f.name != "README.md", f.name))
        if pages:   # folder -> its README page, or its first page (e.g. study-guide/ -> 01-sql.md)
            return os.path.relpath(pages[0], (STAGE / src_rel).parent).replace(os.sep, "/") + anchor
        return f"{GITHUB}/tree/{BRANCH}/{rel_to_root.as_posix()}"
    if repo_target.suffix == ".ipynb" and staged.with_suffix(".html").exists():
        return os.path.relpath(staged.with_suffix(".html"), (STAGE / src_rel).parent).replace(os.sep, "/") + anchor
    if staged.exists():
        return target
    return f"{GITHUB}/blob/{BRANCH}/{rel_to_root.as_posix()}{anchor}"


def transform_markdown():
    for md in STAGE.rglob("*.md"):
        rel = md.relative_to(STAGE)
        if rel.parts[0] in ("playground", "flashcards"):
            continue
        text = md.read_text(encoding="utf-8")
        text = text.replace("<details>", '<details markdown="1">')          # render markdown inside <details>
        text = LINK_RE.sub(lambda m: m.group(1) + rewrite_target(m.group(2), rel) + m.group(3), text)
        text = HREF_RE.sub(lambda m: m.group(1) + rewrite_target(m.group(2), rel) + m.group(3), text)
        if rel.as_posix() == "README.md":
            text = text.replace("# JOBPREP_DA: Data Analyst interview prep kit", "# JOBPREP_DA", 1)
        md.write_text(text, encoding="utf-8")


def main():
    stage_files()
    n_cards = build_flashcards()
    n_q = build_playground()
    render_notebook()
    transform_markdown()
    print(f"Staged site in {STAGE.relative_to(ROOT)}: {n_q} playground questions, {n_cards} flashcards, "
          f"{sum(1 for _ in STAGE.rglob('*.md'))} pages. Links to unpublished files point at {GITHUB}")


if __name__ == "__main__":
    main()
