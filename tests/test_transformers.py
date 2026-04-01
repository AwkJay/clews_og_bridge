from __future__ import annotations
import pandas as pd
import pytest
from clews_og_bridge.transformers import ProductivityTransformer, ProductionWeightsTransformer
from clews_og_bridge.config import MappingConfig

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "technology": ["SolarPV", "Wind", "SolarPV", "Wind"],
        "year": [2020, 2020, 2021, 2021],
        "value": [100.0, 100.0, 120.0, 130.0]
    })

@pytest.fixture
def config():
    return MappingConfig(
        technology_to_sector={"SolarPV": "energy", "Wind": "energy"},
        sector_to_industry={"energy": "utilities"},
        cost_elasticities={"energy": 0.5},
        baseline_sectoral_costs={"energy": 200.0}
    )

def test_productivity_transformer(sample_df, config):
    transformer = ProductivityTransformer()
    mapped_df, trace = transformer.transform(sample_df, config, "total_discounted_cost")
    
    # Aggregated value for 2020: 100 + 100 = 200
    # Z = (C_base / C_curr)^alpha = (200 / 200)^0.5 = 1.0
    val_2020 = mapped_df[mapped_df["year"] == 2020]["value"].iloc[0]
    assert val_2020 == 1.0
    
    # Aggregated value for 2021: 120 + 130 = 250
    # Z = (200 / 250)^0.5 = 0.8^0.5 approx 0.8944
    val_2021 = mapped_df[mapped_df["year"] == 2021]["value"].iloc[0]
    assert pytest.approx(val_2021) == (200.0 / 250.0)**0.5
    
    assert trace["transformation_type"] == "productivity_relative_to_cost"
    assert trace["baseline_source"] == "Configured per sector"

def test_production_weights_transformer(sample_df, config):
    # Add another sector to test normalization
    df = pd.concat([
        sample_df,
        pd.DataFrame({
            "technology": ["Truck"],
            "year": [2020],
            "value": [200.0]
        })
    ], ignore_index=True)
    
    config.technology_to_sector["Truck"] = "transport"
    
    transformer = ProductionWeightsTransformer()
    mapped_df, trace = transformer.transform(df, config, "total_annual_technology_activity")
    
    # 2020: energy (200) + transport (200) = 400
    # energy share = 200 / 400 = 0.5
    # transport share = 200 / 400 = 0.5
    val_energy_2020 = mapped_df[(mapped_df["year"] == 2020) & (mapped_df["sector"] == "energy")]["value"].iloc[0]
    assert val_energy_2020 == 0.5
    
    assert trace["transformation_type"] == "sector_production_weight_normalization"
