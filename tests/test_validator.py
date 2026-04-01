from __future__ import annotations

"""Tests for schema and strict validation."""

from pathlib import Path
import shutil
import sys
import yaml

from pydantic import ValidationError as PydanticValidationError
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from clews_og_bridge.reader import read_clews_csvs
from clews_og_bridge.normalizer import normalize_clews_data
from clews_og_bridge.mapper import map_clews_to_og_params
from clews_og_bridge.config import MappingConfig
from clews_og_bridge.validator import ValidationGate
from clews_og_bridge.models import Metadata


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


def _valid_exchange_data(data_dir: Path, config: MappingConfig) -> dict:
    raw_data = read_clews_csvs(data_dir)
    normalized_data = normalize_clews_data(raw_data)
    clews_data, og_data = map_clews_to_og_params(normalized_data, config)
    metadata = Metadata(run_id="run_1", scenario="test")

    return {
        "metadata": metadata.model_dump(mode="json"),
        "clews_outputs": clews_data,
        "og_parameters": og_data
    }


def test_validator_accepts_valid_instance(data_dir: Path, config: MappingConfig) -> None:
    instance = _valid_exchange_data(data_dir, config)
    validator = ValidationGate()
    validator.validate_final_exchange(instance)


def test_validator_strict_non_numeric_value(data_dir: Path, config: MappingConfig) -> None:
    instance = _valid_exchange_data(data_dir, config)
    # Use the new target parameter name 'Z' and mapped industry 'utilities'
    instance["og_parameters"]["parameters"]["Z"]["value"]["utilities"]["2020"] = "bad"
    validator = ValidationGate()
    with pytest.raises(PydanticValidationError) as excinfo:
        validator.validate_final_exchange(instance)
    message = str(excinfo.value)
    assert "parameters" in message
    assert "Z" in message
    assert "value" in message
    assert "utilities" in message
    assert "2020" in message
