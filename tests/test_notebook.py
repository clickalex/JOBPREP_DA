"""The portfolio notebook must run top-to-bottom on a fresh checkout (slow: ~1 min)."""
import pytest

from conftest import ROOT

NB = ROOT / "portfolio" / "shopkart-growth-analysis" / "analysis.ipynb"


@pytest.mark.slow
def test_notebook_executes_without_errors():
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    nb = nbformat.read(NB, as_version=4)
    nbclient.NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(NB.parent)}}).execute()
    errors = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.output_type == "error"]
    assert not errors
