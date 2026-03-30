from __future__ import annotations
import logging
from typing import Tuple, Set
import pandas as pd
from ..config import MappingConfig

def map_tech_to_sector(df: pd.DataFrame, config: MappingConfig) -> Tuple[pd.DataFrame, Set[str]]:
    """Maps technologies to sectors based on configuration."""
    mapped = df.copy()
    unmapped = []
    
    sectors = []
    for tech in mapped["technology"]:
        sector = config.technology_to_sector.get(tech)
        if sector is None:
            unmapped.append(tech)
            sector = "unmapped"
        sectors.append(sector)
    
    mapped["sector"] = sectors
    mapped = mapped.drop(columns=["technology"])
    
    if unmapped:
        unique_unmapped = set(unmapped)
        msg = f"Unmapped technologies found: {unique_unmapped}"
        if config.unmapped_policy == "fail":
            raise ValueError(msg)
        logging.getLogger(__name__).warning(msg)
        mapped = mapped[mapped["sector"] != "unmapped"]

    return mapped, set(mapped["sector"].unique())

def map_sector_to_industry(df: pd.DataFrame, config: MappingConfig) -> pd.DataFrame:
    """Maps sectors to industries based on configuration."""
    mapped = df.copy()
    industries = []
    for sector in mapped["sector"]:
        industry = config.sector_to_industry.get(sector, sector)
        industries.append(industry)
    
    mapped["industry"] = industries
    return mapped.drop(columns=["sector"])
