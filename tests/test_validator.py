from __future__ import annotations

"""Tests for schema and strict validation."""

from pathlib import Path
import shutil
import sys

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reader import read_clews_csvs
from transformer import transform_to_og_params
from validator import validate_schema, validate_strict


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


def _valid_instance(data_dir: Path) -> dict:
    dataframes = read_clews_csvs(data_dir)
    return transform_to_og_params(dataframes)


def test_validator_accepts_valid_instance(data_dir: Path) -> None:
    instance = _valid_instance(data_dir)
    schema_path = PROJECT_ROOT / "schemas" / "exchange_v1.json"
    validate_schema(instance, schema_path)
    validate_strict(instance)


def test_validator_schema_missing_years(data_dir: Path) -> None:
    instance = _valid_instance(data_dir)
    instance.pop("years")
    schema_path = PROJECT_ROOT / "schemas" / "exchange_v1.json"
    with pytest.raises(JsonSchemaValidationError):
        validate_schema(instance, schema_path)


def test_validator_strict_non_numeric_value(data_dir: Path) -> None:
    instance = _valid_instance(data_dir)
    instance["parameters"]["total_discounted_cost"]["SolarPV"]["2020"] = "bad"
    with pytest.raises(PydanticValidationError) as excinfo:
        validate_strict(instance)
    message = str(excinfo.value)
    assert "total_discounted_cost" in message
    assert "SolarPV" in message
    assert "2020" in message
