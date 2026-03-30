from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import logging

from .models import ExchangeModel


def write_exchange_json(
    model: ExchangeModel, output_path: Path, pretty: bool = True
) -> None:
    """
    Validate and write an exchange JSON file atomically.

    Args:
        model: Pydantic ExchangeModel.
        output_path: Target file path.
        pretty: Whether to format JSON with indentation.
    """
    output_path = Path(output_path)
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    indent = 2 if pretty else None
    temp_path: Path | None = None

    try:
        # Pydantic's model_dump_json ensures we have a valid JSON payload
        payload = model.model_dump_json(indent=indent)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=output_path.parent,
            suffix=output_path.suffix,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        temp_path.replace(output_path)
        logging.getLogger(__name__).info("Wrote exchange file to %s", output_path)

    except Exception as e:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        logging.getLogger(__name__).error("Failed to write exchange file: %s", e)
        raise
