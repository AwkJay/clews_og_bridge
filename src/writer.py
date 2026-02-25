from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from validator import validate_schema


def write_exchange_json(
    instance: dict, output_path: Path, pretty: bool = True
) -> None:
    """
    Validate and write an exchange JSON file atomically.

    Args:
        instance: JSON-compatible exchange data.
        output_path: Target file path.
        pretty: Whether to format JSON with indentation.
    """
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "exchange_v1.json"
    validate_schema(instance, schema_path)

    output_path = Path(output_path)
    indent = 2 if pretty else None
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=output_path.parent,
            suffix=output_path.suffix,
        ) as handle:
            temp_path = Path(handle.name)
            json.dump(instance, handle, indent=indent, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(output_path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise
