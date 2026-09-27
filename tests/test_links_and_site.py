"""Docs integrity: relative links + anchors resolve on GitHub, and generated site assets stay in sync."""
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

from conftest import ROOT, load_module

MD_FILES = [p for p in ROOT.rglob("*.md")
            if not any(part.startswith((".", "_")) or part in ("node_modules", "website") for part in p.relative_to(ROOT).parts)]
LINK_RE = re.compile(r"\]\(([^)\s]+)\)|<a href=\"([^\"]+)\"")   # any ](target) incl. images/badges


def github_slug(heading: str) -> str:
    s = re.sub(r"<[^>]+>", "", heading).strip().lower()
    s = re.sub(r"[`*_~]|\[([^\]]*)\]\([^)]*\)", lambda m: m.group(1) or "", s)
    s = "".join(ch for ch in s if ch in " -" or unicodedata.category(ch)[0] in "LN" or ch == "_")
    return s.replace(" ", "-")


def anchors(md: Path):
    seen, out = {}, set()
    in_code = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            slug = github_slug(m.group(1))
            n = seen.get(slug, 0)
            out.add(slug if n == 0 else f"{slug}-{n}")
            seen[slug] = n + 1
    return out


def links(md: Path):
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    for m in LINK_RE.finditer(text):
        yield next(g for g in m.groups() if g)


def test_md_files_found():
    assert len(MD_FILES) >= 20


@pytest.mark.parametrize("md", MD_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(md):
    broken = []
    for target in links(md):
        if re.match(r"^[a-z]+:", target) or target.startswith("//"):
            continue
        path, _, frag = target.partition("#")
        dest = (md.parent / path).resolve() if path else md
        if not dest.exists():
            broken.append(target)
        elif frag and dest.suffix == ".md" and frag not in anchors(dest):
            broken.append(f"{target} (missing anchor)")
    assert not broken, f"{md.relative_to(ROOT)}: {broken}"


# --------------------------------------------------------------------------- website
site = load_module("build_site", ROOT / "website" / "build_site.py")


def test_flashcards_csv_in_sync(tmp_path):
    cards = site.extract_flashcards()
    assert len(cards) >= 30
    site.write_flashcards(cards, tmp_path / "f.csv")
    committed = (ROOT / "study-guide" / "flashcards.csv").read_text(encoding="utf-8")
    assert (tmp_path / "f.csv").read_text(encoding="utf-8") == committed, "run: python website/build_site.py"


@pytest.fixture(scope="module")
def staged():
    site.main()
    return site.STAGE


def test_playground_json_matches_question_bank(staged):
    from questions import QUESTIONS
    data = json.loads((staged / "playground" / "questions.json").read_text(encoding="utf-8"))
    assert [q["id"] for q in data] == [q["id"] for q in QUESTIONS]
    assert all(q["expected"]["columns"] and "<p>" in q["prompt_html"] for q in data)


def test_mock_interview_questions_extracted():
    import sqlite3
    mock = site.extract_mock_questions()
    assert [q["id"] for q in mock] == [f"m{i}" for i in range(1, 8)]
    con = sqlite3.connect(ROOT / "data" / "shopkart.db")
    for q in mock:
        assert q["prompt_html"].startswith("<p>") and q["hints"] and q["minutes"] > 0, q["id"]
        con.execute(q["solution"]).fetchall()          # answer-key SQL runs
    assert sum(len(q["followups"]) for q in mock) >= 5
    assert all(f["answer"] for q in mock for f in q["followups"]), "every follow-up needs a model answer"


def test_staged_links_point_somewhere_valid(staged):
    for md in staged.rglob("*.md"):
        for target in links(md):
            assert ".ipynb" not in target or target.startswith("https://"), (md, target)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_browser_playground_grader_with_sqljs(staged):
    r = subprocess.run(["node", str(ROOT / "tests" / "playground.test.js")], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_mkdocs_strict_build(staged, tmp_path):
    pytest.importorskip("mkdocs")
    pytest.importorskip("material")
    r = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(ROOT / "website" / "mkdocs.yml"), "-d", str(tmp_path / "s")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-3000:]
    assert (tmp_path / "s" / "playground" / "index.html").exists()
    assert (tmp_path / "s" / "portfolio" / "shopkart-growth-analysis" / "analysis.html").exists()
