from __future__ import annotations

"""Tests for CLEWS to OG parameter mapping."""

from pathlib import Path
import shutil
import sys
import yaml

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from clews_og_bridge.reader import read_clews_csvs
from clews_og_bridge.normalizer import normalize_clews_data
from clews_og_bridge.mapper import map_clews_to_og_params
from clews_og_bridge.config import MappingConfig


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


@pytest.fixture()
def config() -> MappingConfig:
    project_root = Path(__file__).resolve().parents[1]
    mapping_file = project_root / "configs" / "mapping.yaml"
    with open(mapping_file, "r") as f:
        config_dict = yaml.safe_load(f)
    return MappingConfig.model_validate(config_dict)


def test_mapping_logic(data_dir: Path, config: MappingConfig) -> None:
    raw_data = read_clews_csvs(data_dir)
    normalized_data = normalize_clews_data(raw_data)
    clews_data, og_data = map_clews_to_og_params(normalized_data, config)

    # 1. Check years and technologies are collected
    assert clews_data["years"] == [2020, 2021]
    assert "SolarPV" in clews_data["technologies"]

    # 2. Check semantic mapping to industries (utilities, transportation)
    assert "Z" in og_data["parameters"]
    assert "alpha_production" in og_data["parameters"]
    
    # 'energy' mapped to 'utilities' in mapping.yaml
    assert "utilities" in og_data["parameters"]["Z"]["value"]
    
    # 3. Check values are mapped (spot check Z)
    # TotalDiscountedCost: SolarPV 2020: 120.0, Wind 2020: 110.0
    # Aggregated energy cost 2020: 230.0
    # Baseline energy cost: 100.0 (from mapping.yaml)
    # Elasticity energy: 0.3
    # Z = (C_base / C_curr) ^ alpha = (100 / 230) ^ 0.3
    expected_z = (100.0 / 230.0) ** 0.3
    val = og_data["parameters"]["Z"]["value"]["utilities"]["2020"]
    assert pytest.approx(val) == expected_z

    # 4. Check normalization (alpha_production)
    assert og_data["parameters"]["alpha_production"]["value"]["utilities"]["2020"] == 1.0
    
    # 5. Check trace
    assert og_data["mapping_trace"]["Z"]["target_parameter"] == "Z"
    assert og_data["mapping_trace"]["Z"]["elasticity_used"] == 0.3
