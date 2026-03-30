from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd

from .config import MappingConfig, INJECTION_CONTRACT
from .transformers import ProductivityTransformer, ProductionWeightsTransformer, EconomicTransformer
from .transformers.utils import map_sector_to_industry


def map_clews_to_og_params(
    normalized_data: Dict[str, pd.DataFrame], config: MappingConfig
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Perform economically corrected and hardened mapping from CLEWS outputs to OG-Core parameters.
    Orchestrates the transformation using variable-specific economic transformers.
    """
    logger = logging.getLogger(__name__)

    all_years = sorted({int(y) for df in normalized_data.values() for y in df["year"]})
    all_technologies = sorted({str(t) for df in normalized_data.values() for t in df["technology"]})

    clews_outputs_payload: Dict[str, Any] = {
        "years": all_years,
        "technologies": all_technologies,
        "data": {}
    }

    og_parameters_payload: Dict[str, Any] = {
        "parameters": {},
        "mapping_trace": {}
    }

    # Registry of economic transformers
    transformers: Dict[str, EconomicTransformer] = {
        "total_discounted_cost": ProductivityTransformer(),
        "total_annual_technology_activity": ProductionWeightsTransformer(),
    }

    for variable, df in normalized_data.items():
        clews_outputs_payload["data"][variable] = _frame_to_dict(df, "technology")

        _validate_units(variable, config)

        target_param = config.variable_to_parameter.get(variable)
        contract = INJECTION_CONTRACT.get(variable)
        
        if target_param is None or target_param.lower() == "none" or contract is None:
            logger.info("Variable '%s' has no target OG parameter injection contract. Skipping.", variable)
            continue

        transformer = transformers.get(variable)
        if transformer is None:
            logger.warning("No economic transformer defined for variable '%s'.", variable)
            continue

        # 1. Economic Transformation (Physical -> Proxy)
        mapped_df, trace = transformer.transform(df, config, variable)
        
        # 2. Structural Mapping (Sector -> Industry)
        mapped_df = map_sector_to_industry(mapped_df, config)

        # 3. Economic Sanity Checks & Hard Constraints
        _apply_hard_constraints(mapped_df, target_param, config, all_years)

        # 4. Final Payload Assembly
        og_parameters_payload["parameters"][target_param] = {
            "value": _frame_to_dict(mapped_df, "industry"),
            "dimensions": {
                "names": contract["dimensions"],
                "industry_indices": config.industry_indices
            },
            "units": contract["output_units"],
            "og_core_meaning": contract["meaning"]
        }
        
        og_parameters_payload["mapping_trace"][target_param] = {
            "source_variable": variable,
            "target_parameter": target_param,
            "economic_interpretation": contract["role"],
            "injection_location": contract["injection_location"],
            "parameter_role": contract["parameter_role"],
            "transformation_type": trace["transformation_type"],
            "formula": contract["formula"],
            "input_unit": config.units_contract.get(variable, "unknown"),
            "aggregation_rule": contract["aggregation"],
            "baseline_reference": trace.get("baseline_source"),
            "elasticity_used": trace.get("elasticity_value")
        }

    return clews_outputs_payload, og_parameters_payload


def _apply_hard_constraints(df: pd.DataFrame, target_param: str, config: MappingConfig, expected_years: List[int]) -> None:
    """Apply economic and structural hard constraints."""
    # 1. Reject Unknown Industries
    industries = df["industry"].unique()
    for ind in industries:
        if ind not in config.sector_to_industry.values():
            raise ValueError(f"Industry '{ind}' is not defined in sector_to_industry mapping.")
        if ind not in config.industry_indices:
            raise ValueError(f"Industry '{ind}' is missing an index mapping in industry_indices.")

    # 2. Reject Missing Years
    actual_years = set(df["year"].unique())
    missing_years = set(expected_years) - actual_years
    if missing_years:
        logging.getLogger(__name__).warning("Parameter '%s' is missing data for years: %s", target_param, missing_years)

    # 3. Numeric constraints
    if (df["value"] <= 0).any():
        if target_param == "Z":
            raise ValueError(f"Productivity Z must be strictly positive. Check input costs and baseline.")
        if (df["value"] < 0).any():
            raise ValueError(f"Negative values detected in parameter '{target_param}'.")

    if target_param == "alpha_production":
        yearly_sums = df.groupby("year")["value"].sum()
        for year, year_sum in yearly_sums.items():
            if not np.isclose(year_sum, 1.0, atol=1e-4):
                raise ValueError(f"Production weights for year {year} sum to {year_sum}, not 1.0.")

    if df["value"].isna().any():
        raise ValueError(f"NaN values detected in parameter '{target_param}'.")
    
    if target_param == "Z":
        for sector, elasticity in config.cost_elasticities.items():
            if not (0.0 <= elasticity <= 1.0):
                raise ValueError(f"Cost elasticity for {sector} must be between 0.0 and 1.0. Found: {elasticity}")


def _validate_units(variable: str, config: MappingConfig) -> None:
    expected = config.units_contract.get(variable)
    if not expected:
        return
    logging.getLogger(__name__).debug("Unit contract for %s: %s", variable, expected)


def _frame_to_dict(df: pd.DataFrame, index_col: str) -> Dict[str, Dict[str, float]]:
    if df.duplicated(subset=[index_col, "year"]).any():
        df = df.groupby([index_col, "year"], as_index=False)["value"].sum()

    pivot_df = df.pivot_table(index=index_col, columns="year", values="value")

    result: Dict[str, Dict[str, float]] = {}
    for idx in pivot_df.index:
        row = pivot_df.loc[idx]
        year_values = {
            str(int(year)): float(value)
            for year, value in row.items()
            if pd.notna(value)
        }
        if year_values:
            result[str(idx)] = year_values
    return result
