from __future__ import annotations

"""Tests for CLEWS to OG parameter transformation."""

from pathlib import Path
import shutil
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reader import read_clews_csvs
from transformer import transform_to_og_params


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


def test_transform_to_og_params_output_shape_and_ordering(data_dir: Path) -> None:
    dataframes = read_clews_csvs(data_dir)
    result = transform_to_og_params(dataframes)

    assert list(result.keys()) == ["years", "technologies", "parameters"]
    assert result["years"] == [2020, 2021]
    assert result["technologies"] == ["SolarPV", "Wind"]
    assert set(result["parameters"].keys()) == {
        "total_discounted_cost",
        "annual_emissions",
        "technology_activity",
    }

    assert result["parameters"]["total_discounted_cost"]["SolarPV"]["2020"] == 120.0
    assert result["parameters"]["total_discounted_cost"]["Wind"]["2020"] == 110.0
    assert result["parameters"]["annual_emissions"]["Wind"]["2021"] == 45.0
    assert result["parameters"]["technology_activity"]["SolarPV"]["2021"] == 290.0
