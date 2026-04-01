from __future__ import annotations

"""Tests for OG-Core compatibility of the generated payload."""

from pathlib import Path
import json
import yaml
import pytest

from clews_og_bridge.pipeline import Pipeline
from clews_og_bridge.config import MappingConfig


def test_og_core_payload_compatibility(tmp_path: Path):
    """
    Simulates how OG-Core would consume the output.
    """
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "tests" / "data"
    mapping_file = project_root / "configs" / "mapping.yaml"
    output_file = tmp_path / "og_compat_payload.json"

    with open(mapping_file, "r") as f:
        config_dict = yaml.safe_load(f)
    config = MappingConfig.model_validate(config_dict)

    pipeline = Pipeline(config)
    model = pipeline.run(
        input_dir=input_dir,
        output_path=output_file,
        scenario="compat_test",
        run_id="compat_001"
    )

    # 1. Check dimensions and industry indices
    assert model.og_parameters.parameters["Z"].dimensions.names == ["time", "industry"]
    assert model.og_parameters.parameters["Z"].dimensions.industry_indices["utilities"] == 0
    
    # 2. Extract the revision dictionary
    og_revision = {
        name: param.value 
        for name, param in model.og_parameters.parameters.items()
    }

    # 3. Validate TFP (Z)
    assert "Z" in og_revision
    assert "utilities" in og_revision["Z"]
    assert og_revision["Z"]["utilities"]["2020"] > 0

    # 4. Check Traceability for policy analysis
    trace = model.og_parameters.mapping_trace["Z"]
    assert trace.injection_location == "update_specifications -> production function"
    assert trace.parameter_role == "scaling factor for sectoral TFP"
    assert "Effective productivity" in trace.economic_interpretation
