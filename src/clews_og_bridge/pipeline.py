from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .reader import read_clews_csvs
from .normalizer import normalize_clews_data
from .mapper import map_clews_to_og_params
from .config import MappingConfig
from .validator import ValidationGate
from .writer import write_exchange_json
from .models import Metadata, ExchangeModel, ClewsOutputs, OgParameters


class Pipeline:
    """The CLEWS-OG-Core Data Bridge Pipeline."""

    def __init__(self, mapping_config: MappingConfig):
        self.mapping_config = mapping_config
        self.validator = ValidationGate()

    def run(
        self,
        input_dir: Path,
        output_path: Path,
        scenario: str,
        run_id: str,
        country: Optional[str] = None
    ) -> ExchangeModel:
        """
        Execute the full pipeline: READ -> NORMALIZE -> MAP -> VALIDATE -> WRITE.
        """
        logger = logging.getLogger(__name__)

        # 1. READ
        raw_data = read_clews_csvs(input_dir)
        self.validator.validate_raw_input(raw_data)

        # 2. NORMALIZE
        normalized_data = normalize_clews_data(raw_data)
        self.validator.validate_normalized_data(normalized_data)

        # 3. MAP
        clews_data, og_data = map_clews_to_og_params(normalized_data, self.mapping_config)

        # 4. PREPARE FINAL PAYLOAD
        metadata = Metadata(
            run_id=run_id,
            scenario=scenario,
            country=country
        )

        exchange_data = {
            "metadata": metadata.model_dump(),
            "clews_outputs": clews_data,
            "og_parameters": og_data
        }

        # 5. VALIDATE
        model = self.validator.validate_final_exchange(exchange_data)

        # 6. WRITE
        write_exchange_json(model, output_path)

        return model
