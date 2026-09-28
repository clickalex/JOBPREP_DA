"""pandas practice: reference solutions pass, stubs are untouched, and the grader catches wrong answers."""
import inspect
import sys
import types

from conftest import ROOT, load_module

PY = ROOT / "practice" / "python"
check = load_module("py_check", PY / "check.py")


def test_reference_solutions_pass(capsys):
    assert check.main(["--solutions"]) == 0
    assert "25 passed" in capsys.readouterr().out


def test_exercise_stubs_are_unsolved(capsys):
    assert check.main([]) == 0
    assert "25 not attempted" in capsys.readouterr().out


def test_wrong_answers_are_caught(capsys, monkeypatch):
    """Swap in an 'exercises' module where p01 drops a row: exactly one failure must be reported."""
    import solutions
    fake = types.ModuleType("exercises")
    for name in dir(solutions):
        if name.startswith("p") and name[1:3].isdigit():
            setattr(fake, name, getattr(solutions, name))
    p01_name = next(n for n in dir(solutions) if n.startswith("p01"))
    p01 = getattr(solutions, p01_name)

    def wrong(*args, **kwargs):
        return p01(*args, **kwargs).iloc[1:]

    wrong.__signature__ = inspect.signature(p01)       # the checker passes inputs by parameter name
    setattr(fake, p01_name, wrong)
    monkeypatch.setitem(sys.modules, "exercises", fake)
    assert check.main([]) == 1
    out = capsys.readouterr().out
    assert "24 passed" in out and "1 failed" in out
