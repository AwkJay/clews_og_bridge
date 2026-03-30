from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from .pipeline import Pipeline
from .config import MappingConfig


@click.group()
def cli():
    """CLEWS-OG-Core Data Bridge Pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@cli.command(name="run")
@click.option("--input-dir", "-i", type=click.Path(exists=True, path_type=Path), required=True, help="Directory containing CLEWS CSVs.")
@click.option("--mapping-file", "-m", type=click.Path(exists=True, path_type=Path), required=True, help="YAML mapping configuration file.")
@click.option("--output-file", "-o", type=click.Path(path_type=Path), required=True, help="Output JSON exchange file.")
@click.option("--scenario", "-s", type=str, required=True, help="Scenario name.")
@click.option("--run-id", "-r", type=str, required=True, help="Unique run identifier.")
@click.option("--country", "-c", type=str, help="Country code.")
def run_pipeline(
    input_dir: Path,
    mapping_file: Path,
    output_file: Path,
    scenario: str,
    run_id: str,
    country: Optional[str]
):
    """Run the CLEWS to OG-Core mapping pipeline."""
    try:
        # 1. Load mapping config
        with open(mapping_file, "r") as f:
            config_dict = yaml.safe_load(f)
        config = MappingConfig.model_validate(config_dict)

        # 2. Run pipeline
        pipeline = Pipeline(config)
        pipeline.run(
            input_dir=input_dir,
            output_path=output_file,
            scenario=scenario,
            run_id=run_id,
            country=country
        )
        click.echo(f"Pipeline finished successfully. Output: {output_file}")
        sys.exit(0)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
