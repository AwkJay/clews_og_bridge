# clews_og_bridge

This repository contains a small Python project that helps bridge data between **CLEWS model outputs** and **OG-Core style datasets**.

The main purpose of this project is to read CSV outputs produced by CLEWS/OSeMOSYS energy system models and convert them into a structured format that can be used in economic modeling workflows. Since these models often use different data layouts, the tool provides a simple pipeline that standardizes and validates the data before exporting it as a JSON exchange file.

The codebase is written for **Python 3.12** and has been tested primarily on **Windows 11**, although it should work on other platforms as well.

---

## What the project does

The pipeline performs four main steps:

1. **Read** CLEWS output tables from CSV files.
2. **Transform** the tables into a consistent internal structure.
3. **Validate** the resulting dataset using JSON Schema and Pydantic models.
4. **Write** the validated data to a portable JSON exchange file.

The goal is to reduce manual data preparation when connecting energy system models with macroeconomic models.

---

## Project structure

```
clews_og_bridge/

src/
    reader.py        # loads and normalizes CLEWS CSV outputs
    transformer.py   # converts tables into the exchange structure
    validator.py     # schema and type validation
    writer.py        # safe JSON export

schemas/
    exchange_v1.json

examples/
    run_pipeline.py  # simple CLI pipeline example

tests/
    unit tests and sample data
```

---

## Installation

Create a virtual environment and install dependencies.

```
pip install -r requirements.txt
```

You can then import the package in Python:

```
import clews_og_bridge
```

---

## Running the example pipeline

A small CLI example is provided in the `examples` directory.

```
python examples/run_pipeline.py <input_directory> <output_file>
```

The script reads the CLEWS CSV files from the input directory and writes the processed JSON exchange file.

---

## Notes for Windows users

Paths in the project use Python's `pathlib` module to avoid issues with Windows path separators.

Example:

```
from pathlib import Path

input_dir = Path(r"C:\data") / "inputs"
```

---

## Motivation

Energy system models and macroeconomic models are often used together in policy analysis, but their data formats are usually not directly compatible. This project is a small attempt to simplify that connection by providing a consistent way to transform and validate CLEWS outputs before passing them to other tools.

The repository mainly serves as an experimental data bridge and a starting point for building reproducible pipelines between energy and economic modeling workflows.
