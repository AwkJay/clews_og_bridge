from __future__ import annotations

"""Tests for CLEWS CSV reader utilities."""

from pathlib import Path
import shutil
import sys

from pandas.api.types import is_float_dtype, is_integer_dtype, is_object_dtype
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reader import read_clews_csvs


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

    for frame in result.values():
        assert list(frame.columns) == ["year", "technology", "value"]
        assert is_integer_dtype(frame["year"])
        assert is_object_dtype(frame["technology"])
        assert is_float_dtype(frame["value"])
