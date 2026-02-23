from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate
from pydantic import BaseModel, ValidationError, field_validator
from pydantic.config import ConfigDict


class ParametersModel(BaseModel):
    total_discounted_cost: dict[str, dict[str, float]] | None = None
    annual_emissions: dict[str, dict[str, float]] | None = None
    technology_activity: dict[str, dict[str, float]] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "total_discounted_cost",
        "annual_emissions",
        "technology_activity",
        mode="before",
    )
    @classmethod
    def _validate_numeric_values(cls, value: Any, info) -> Any:
        if value is None or not isinstance(value, dict):
            return value
        for technology, years in value.items():
            if not isinstance(years, dict):
                raise ValueError(f"Invalid mapping for {info.field_name}.{technology}")
            for year, number in years.items():
                try:
                    float(number)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Non-numeric value for {info.field_name}.{technology}.{year}"
                    )
        return value


class ExchangeModel(BaseModel):
    years: list[int]
    technologies: list[str]
    parameters: ParametersModel

    model_config = ConfigDict(extra="forbid")


def validate_schema(instance: dict, schema_path: Path) -> None:
    """
    Validate an instance against a JSON Schema file.

    Args:
        instance: Instance data to validate.
        schema_path: Path to the JSON Schema.
    """
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validate(instance=instance, schema=schema)


def validate_strict(instance: dict) -> ExchangeModel:
    """
    Validate and parse an instance with strict typing.

    Args:
        instance: Instance data to validate.

    Returns:
        Parsed ExchangeModel.
    """
    return ExchangeModel.model_validate(instance)
