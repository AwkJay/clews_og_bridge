from __future__ import annotations

"""Tests for CLEWS CSV reader utilities."""

from pathlib import Path
import shutil
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from clews_og_bridge.reader import read_clews_csvs


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    source_dir = Path(__file__).parent / "data"
    for name in [
        "TotalDiscountedCost.csv",
        "AnnualEmissions.csv",
        "TotalAnnualTechnologyActivity.csv",
    ]:
        shutil.copy(source_dir / name, tmp_path / name)
    return tmp_path


def test_read_valid_csvs(data_dir: Path) -> None:
    result = read_clews_csvs(data_dir)

    assert "total_discounted_cost" in result
    assert "annual_emissions" in result
    assert "total_annual_technology_activity" in result

    # Check that we got DataFrames with some content
    for key, frame in result.items():
        assert not frame.empty
        # Verify it has some version of year/tech/value columns
        cols = [c.lower() for c in frame.columns]
        assert any("year" in c for c in cols)
        assert any("tech" in c for c in cols)
        assert any("value" in c for c in cols)
