from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class MappingConfig(BaseModel):
    """YAML mapping configuration structure."""
    technology_to_sector: Dict[str, str]
    # Sector to OG-Core Industry mapping (e.g., energy -> utilities)
    sector_to_industry: Dict[str, str] = Field(default_factory=dict)
    # Industry name to internal OG-Core index mapping
    industry_indices: Dict[str, int] = Field(default_factory=dict)
    
    # sector -> elasticity (alpha in Z = (C_base/C_curr)^alpha)
    cost_elasticities: Dict[str, float] = Field(default_factory=dict)
    
    variable_to_parameter: Dict[str, str] = {
        "total_discounted_cost": "Z",  # Productivity
        "total_annual_technology_activity": "alpha_production",  # Production weights
    }
    
    unmapped_policy: str = "log"
    
    units_contract: Dict[str, str] = {
        "total_discounted_cost": "Million USD",
        "annual_emissions": "Mt CO2",
        "total_annual_technology_activity": "PJ",
    }
    
    # Optional: sector -> baseline cost for Z calculation
    baseline_sectoral_costs: Optional[Dict[str, float]] = None


# Injection Contract for OG-Core update_specifications()
# This defines how a variable is mapped to an OG parameter structurally and semantically.
INJECTION_CONTRACT = {
    "total_discounted_cost": {
        "target": "Z",
        "meaning": "Total Factor Productivity (TFP) level by industry and year.",
        "dimensions": ["time", "industry"],
        "role": "Productivity Proxy: Effective productivity derived from cost signals.",
        "injection_location": "update_specifications -> production function",
        "parameter_role": "scaling factor for sectoral TFP",
        "aggregation": "sum",
        "formula": "Z = (Cost_base / Cost_current)^alpha",
        "output_units": "dimensionless",
    },
    "total_annual_technology_activity": {
        "target": "alpha_production",
        "meaning": "Industry weights in the aggregate production function.",
        "dimensions": ["time", "industry"],
        "role": "Production Weights: Relative importance of sectoral activity in aggregate output.",
        "injection_location": "update_specifications -> aggregator function",
        "parameter_role": "sectoral distribution weight",
        "aggregation": "sum",
        "formula": "Industry Share (Normalized to unity)",
        "output_units": "dimensionless",
    },
}
