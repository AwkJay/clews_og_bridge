from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class InvalidInputError(ValueError):
    pass


def read_clews_csvs(directory: Path, expected_patterns: Optional[Dict[str, str]] = None) -> Dict[str, pd.DataFrame]:
    """
    Read CLEWS CSV files from a directory based on filename patterns.

    Args:
        directory: Directory containing CSV files.
        expected_patterns: Mapping of variable name to filename token.
            Defaults to standard CLEWS outputs.

    Returns:
        Mapping of variable name to raw DataFrame.
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        raise InvalidInputError(f"Directory not found: {directory}")

    csv_files = [path for path in directory.glob("*.csv") if path.is_file()]

    patterns = expected_patterns or {
        "total_discounted_cost": "totaldiscountedcost",
        "annual_emissions": "annualemissions",
        "total_annual_technology_activity": "totalannualtechnologyactivity",
    }

    matched: Dict[str, pd.DataFrame] = {}
    logger = logging.getLogger(__name__)

    for key, token in patterns.items():
        found = False
        for path in csv_files:
            if token.lower() in path.stem.lower():
                logger.info("Reading %s from %s", key, path)
                matched[key] = pd.read_csv(path)
                found = True
                break
        if not found:
            logger.warning("Missing expected CSV for %s in %s", key, directory)

    return matched
