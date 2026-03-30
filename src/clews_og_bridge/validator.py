from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

from jsonschema import validate
from pydantic import ValidationError

from .models import ExchangeModel


class ValidationGate:
    """Validation gate for checking data at different pipeline stages."""

    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path

    def validate_raw_input(self, raw_data: Dict[str, Any]) -> None:
        """Validate raw input data structure."""
        if not raw_data:
            raise ValueError("No raw data found in input directory.")

    def validate_normalized_data(self, normalized_data: Dict[str, Any]) -> None:
        """Validate normalized data structure."""
        if not normalized_data:
            raise ValueError("Normalization produced no output.")

    def validate_final_exchange(self, exchange_data: Dict[str, Any]) -> ExchangeModel:
        """Validate final exchange payload using Pydantic model and optional JSON Schema."""
        try:
            # 1. Strict Pydantic validation
            model = ExchangeModel.model_validate(exchange_data)

            # 2. JSON Schema validation (optional, for backward compatibility)
            if self.schema_path and self.schema_path.exists():
                schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
                validate(instance=exchange_data, schema=schema)

            return model
        except ValidationError as e:
            logging.getLogger(__name__).error("Pydantic validation failed: %s", e)
            raise
        except Exception as e:
            logging.getLogger(__name__).error("Validation failed: %s", e)
            raise
