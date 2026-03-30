from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

import pandas as pd


def normalize_clews_data(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Standardize CLEWS output columns and types.

    Args:
        dataframes: Mapping of variable name to raw DataFrame.

    Returns:
        Mapping of variable name to normalized DataFrame with at least:
        year, technology, value.
    """
    normalized: Dict[str, pd.DataFrame] = {}
    for key, df in dataframes.items():
        normalized[key] = _normalize_columns(df, key)
    return normalized


def _normalize_columns(df: pd.DataFrame, variable_name: str) -> pd.DataFrame:
    required = {
        "year": ["year", "Year", "YEAR"],
        "technology": ["technology", "TECHNOLOGY", "TECH", "Technology"],
        "value": ["value", "VALUE", "Value"],
    }

    column_map: Dict[str, str] = {}
    for standard, variants in required.items():
        match = _find_column(df.columns, variants)
        if match is None:
            raise ValueError(f"Missing required column '{standard}' in {variable_name}")
        column_map[match] = standard

    renamed = df.rename(columns=column_map)

    # Ensure year and value are numeric
    renamed["year"] = pd.to_numeric(renamed["year"], errors="coerce")
    renamed["value"] = pd.to_numeric(renamed["value"], errors="coerce")

    if renamed["year"].isna().any() or renamed["value"].isna().any():
        raise ValueError(f"Non-numeric values in year or value column in {variable_name}")

    renamed["year"] = renamed["year"].astype(int)
    renamed["technology"] = renamed["technology"].astype(str)
    renamed["value"] = renamed["value"].astype(float)

    # Handle duplicates: check if any other dimensions exist
    dimensions = [c for c in renamed.columns if c not in ["value"]]
    if renamed.duplicated(subset=dimensions).any():
        logging.getLogger(__name__).warning(
            "Found duplicate rows for dimensions %s in %s. Aggregating with sum.",
            dimensions, variable_name
        )
        renamed = renamed.groupby(dimensions, as_index=False)["value"].sum()

    return renamed


def _find_column(columns: List[str], variants: List[str]) -> Optional[str]:
    lowered = {name.lower(): name for name in columns}
    for variant in variants:
        candidate = lowered.get(variant.lower())
        if candidate is not None:
            return candidate
    return None
