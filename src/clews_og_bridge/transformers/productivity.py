from __future__ import annotations
from typing import Dict, Any, Tuple
import pandas as pd
from .base import EconomicTransformer
from ..config import MappingConfig

class ProductivityTransformer(EconomicTransformer):
    """
    TFP mapping: Z = (C_base / C_current)^alpha.
    Maps physical costs to productivity shocks.
    """
    
    def transform(self, df: pd.DataFrame, config: MappingConfig, var_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        # First map tech to sector (this is a shared utility, we'll keep it in a common place later)
        from .utils import map_tech_to_sector
        
        mapped, sectors_found = map_tech_to_sector(df, config)
        aggregated = mapped.groupby(["sector", "year"], as_index=False)["value"].sum()
        
        trace_baseline = "None"
        avg_elasticity = 0.0
        
        for sector in sectors_found:
            mask = aggregated["sector"] == sector
            sector_data = aggregated[mask]
            
            if sector_data.empty:
                continue

            if config.baseline_sectoral_costs and sector in config.baseline_sectoral_costs:
                c_base = config.baseline_sectoral_costs[sector]
                trace_baseline = "Configured per sector"
            else:
                first_year = sector_data["year"].min()
                c_base = sector_data[sector_data["year"] == first_year]["value"].iloc[0]
                trace_baseline = f"Auto-computed from first year ({first_year})"
                
            alpha = config.cost_elasticities.get(sector, 1.0)
            avg_elasticity = alpha 
            
            aggregated.loc[mask, "value"] = (c_base / aggregated.loc[mask, "value"]).pow(alpha)

        trace = {
            "transformation_type": "productivity_relative_to_cost",
            "baseline_source": trace_baseline,
            "elasticity_value": avg_elasticity,
            "sectors_mapped": list(sectors_found)
        }
        return aggregated, trace
