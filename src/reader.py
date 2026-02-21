from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd


class InvalidInputError(ValueError):
    pass


def read_clews_csvs(directory: Path) -> dict[str, pd.DataFrame]:
    """
    Read recognized CLEWS CSV files from a directory.

    Args:
        directory: Directory containing CSV files.

    Returns:
        Mapping of dataset key to DataFrame with columns: year, technology, value.
    """
    directory = Path(directory)
    csv_files = [path for path in directory.glob("*.csv") if path.is_file()]

    patterns = {
        "total_discounted_cost": "totaldiscountedcost",
        "annual_emissions": "annualemissions",
        "total_annual_technology_activity": "totalannualtechnologyactivity",
    }

    matched: dict[str, Path] = {}
    for path in csv_files:
        name = path.stem.lower()
        for key, token in patterns.items():
            if name.startswith(token):
                matched[key] = path

    logger = logging.getLogger(__name__)
    for key in patterns:
        if key not in matched:
            logger.warning("Missing expected CSV for %s in %s", key, directory)

    result: dict[str, pd.DataFrame] = {}
    for key, path in matched.items():
        df = pd.read_csv(path)
        normalized = _normalize_columns(df)
        result[key] = normalized

    return result


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "year": ["year", "Year", "YEAR"],
        "technology": ["technology", "TECHNOLOGY", "TECH", "Technology"],
        "value": ["value", "VALUE", "Value"],
    }

    column_map: dict[str, str] = {}
    for standard, variants in required.items():
        match = _find_column(df.columns, variants)
        if match is None:
            raise InvalidInputError(f"Missing required column: {standard}")
        column_map[match] = standard

    renamed = df.rename(columns=column_map)
    normalized = renamed[list(required.keys())].copy()

    normalized["year"] = pd.to_numeric(normalized["year"], errors="coerce")
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")
    if normalized["year"].isna().any() or normalized["value"].isna().any():
        raise InvalidInputError("Non-numeric values in year or value column")

    normalized["year"] = normalized["year"].astype(int)
    normalized["technology"] = normalized["technology"].astype(str)
    normalized["value"] = normalized["value"].astype(float)

    if len(normalized) < 1 or list(normalized.columns) != ["year", "technology", "value"]:
        raise InvalidInputError("Invalid input shape")

    return normalized


def _find_column(columns: Iterable[str], variants: Iterable[str]) -> str | None:
    lowered = {name.lower(): name for name in columns}
    for variant in variants:
        candidate = lowered.get(variant.lower())
        if candidate is not None:
            return candidate
    return None
