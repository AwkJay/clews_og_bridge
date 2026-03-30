from __future__ import annotations
from typing import Dict, Any, Tuple
import pandas as pd
from .base import EconomicTransformer
from ..config import MappingConfig

class ProductionWeightsTransformer(EconomicTransformer):
    """
    Activity to Production Weights: normalized to yearly sum of 1.0.
    """
    
    def transform(self, df: pd.DataFrame, config: MappingConfig, var_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        from .utils import map_tech_to_sector
        
        mapped, sectors_found = map_tech_to_sector(df, config)
        aggregated = mapped.groupby(["sector", "year"], as_index=False)["value"].sum()
        
        yearly_totals = aggregated.groupby("year")["value"].transform("sum")
        aggregated["value"] = aggregated["value"] / yearly_totals

        trace = {
            "transformation_type": "sector_production_weight_normalization",
            "sectors_mapped": list(sectors_found)
        }
        return aggregated, trace
