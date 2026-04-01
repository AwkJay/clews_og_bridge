from __future__ import annotations

import json
from pathlib import Path
import yaml
import pytest

from clews_og_bridge.pipeline import Pipeline
from clews_og_bridge.config import MappingConfig


def test_full_pipeline_execution(tmp_path: Path):
    # 1. Setup paths
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "tests" / "data"
    mapping_file = project_root / "configs" / "mapping.yaml"
    output_file = tmp_path / "exchange_payload.json"

    # 2. Load config
    with open(mapping_file, "r") as f:
        config_dict = yaml.safe_load(f)
    config = MappingConfig.model_validate(config_dict)

    # 3. Run pipeline
    pipeline = Pipeline(config)
    model = pipeline.run(
        input_dir=input_dir,
        output_path=output_file,
        scenario="test_scenario",
        run_id="run_123",
        country="US"
    )

    # 4. Assertions on the model
    assert model.metadata.run_id == "run_123"
    assert model.metadata.scenario == "test_scenario"
    assert model.metadata.country == "US"

    assert "total_discounted_cost" in model.clews_outputs.data
    # 'energy' mapped to 'utilities' in mapping.yaml
    assert "utilities" in model.og_parameters.parameters["Z"].value

    # 5. Assertions on the output file
    assert output_file.exists()
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data["metadata"]["run_id"] == "run_123"
        assert "clews_outputs" in data
        assert "og_parameters" in data
        # Check trace existence
        assert "Z" in data["og_parameters"]["mapping_trace"]
