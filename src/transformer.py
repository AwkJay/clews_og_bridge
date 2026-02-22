from __future__ import annotations

from typing import Any

import pandas as pd


def variable_name_normalizer(name: str) -> str:
    """
    Normalize a variable name to an alphanumeric lowercase token.

    Args:
        name: Original variable name.

    Returns:
        Normalized token used for mapping.
    """
    return "".join(ch for ch in name.lower() if ch.isalnum())


def transform_to_og_params(dataframes: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """
    Transform CLEWS-style tables into an OG-Core-like parameter dictionary.

    Args:
        dataframes: Mapping of variable name to DataFrame with columns
            year, technology, value.

    Returns:
        OG-Core-like parameter payload with years, technologies, and parameters.
    """
    mapping = {
        "totaldiscountedcost": "total_discounted_cost",
        "annualemissions": "annual_emissions",
        "totalannualtechnologyactivity": "technology_activity",
    }

    normalized_frames: dict[str, pd.DataFrame] = {}
    for variable_name, frame in dataframes.items():
        normalized_name = variable_name_normalizer(variable_name)
        target_key = mapping.get(normalized_name)
        if target_key is None:
            continue
        normalized_frames[target_key] = frame

    years = sorted(
        {
            int(year)
            for frame in normalized_frames.values()
            for year in frame["year"].tolist()
        }
    )
    technologies = sorted(
        {
            str(technology)
            for frame in normalized_frames.values()
            for technology in frame["technology"].tolist()
        }
    )

    parameters: dict[str, dict[str, dict[str, float]]] = {}
    for target_key, frame in normalized_frames.items():
        parameters[target_key] = _frame_to_parameter_dict(frame, years, technologies)

    return {
        "years": years,
        "technologies": technologies,
        "parameters": parameters,
    }


def _frame_to_parameter_dict(
    frame: pd.DataFrame, years: list[int], technologies: list[str]
) -> dict[str, dict[str, float]]:
    parameter_values: dict[str, dict[str, float]] = {}
    for technology in technologies:
        subset = frame[frame["technology"].astype(str) == technology]
        if subset.empty:
            continue
        year_values: dict[str, float] = {}
        for year in years:
            selected = subset[subset["year"].astype(int) == year]
            if selected.empty:
                continue
            year_values[str(year)] = float(selected.iloc[-1]["value"])
        if year_values:
            parameter_values[technology] = year_values
    return parameter_values
