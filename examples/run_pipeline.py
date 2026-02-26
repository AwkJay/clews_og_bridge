from __future__ import annotations

import sys
from pathlib import Path

import click

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from reader import read_clews_csvs
from transformer import transform_to_og_params
from validator import validate_schema, validate_strict
from writer import write_exchange_json


@click.command(name="run-pipeline")
@click.argument("input_dir", type=click.Path(path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
def run_pipeline(input_dir: Path, output_file: Path) -> None:
    dataframes = read_clews_csvs(input_dir)
    instance = transform_to_og_params(dataframes)
    validate_strict(instance)
    schema_path = PROJECT_ROOT / "schemas" / "exchange_v1.json"
    validate_schema(instance, schema_path)
    write_exchange_json(instance, output_file)
    click.echo(
        f"Success: wrote {len(instance['years'])} years and {len(instance['technologies'])} technologies."
    )


def main() -> None:
    try:
        run_pipeline(standalone_mode=False)
        sys.exit(0)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
