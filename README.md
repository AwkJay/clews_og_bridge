# CLEWS → OG-Core Semantic Integration Bridge

A structured, validated transformation layer that maps CLEWS physical system outputs into economically meaningful OG-Core parameters.

## The Problem

CLEWS and OG-Core operate on fundamentally different abstractions. 

- **CLEWS** → physical system (energy, emissions, technologies) 
- **OG-Core** → macroeconomic equilibrium (TFP, sectoral production) 

The challenge is not data format conversion — it is **semantic translation**. 

Naively passing outputs between the models leads to: 
- incorrect economic interpretation 
- unstable model behavior 
- misleading policy conclusions 

This project focuses on solving that gap explicitly.

## What This Project Does

This repository implements a semantic transformation pipeline that: 

1. Parses CLEWS outputs (CSV) 
2. Normalizes units and structure 
3. Applies explicit economic mappings 
4. Validates data (structural + numeric + economic) 
5. Produces OG-Core-compatible parameter inputs 

The system is designed to be: 
- transparent 
- configurable 
- reproducible 
- extensible 

## Why This Matters 

Energy–economy modeling is used to guide real policy decisions. 

If the integration between models is incorrect: 
- emissions policies can appear effective when they are not 
- economic impacts can be misestimated 
- cross-sector feedback loops are missed entirely 

This project ensures that: 
- physical system outputs are translated into economically meaningful signals 
- assumptions are explicit and auditable 
- model coupling does not introduce silent errors 

In short, this is about making integrated policy modeling **trustworthy**. 

This becomes especially important in multi-sector policy analysis, where errors in one model propagate across the entire system.

## Architecture Overview

The system is structured into modular layers: 

CLEWS CSV → Parser → Normalizer → Mapper → Validator → OG-Core Parameters

### Pipeline Flow (Simplified) 

```text
CLEWS CSV 
   ↓ 
Parser → Normalizer → Mapper → Validator 
   ↓ 
OG-Core Parameter Payload 
```

Each stage enforces constraints before passing data forward. 

This ordering ensures that invalid assumptions are detected early, before they propagate into model execution.

### Key Components

- [pipeline.py](clews_og_bridge/pipeline.py) → execution flow 
- [mapper.py](clews_og_bridge/mapper.py) → orchestration layer 
- [transformers/](clews_og_bridge/transformers/) → economic logic 
- [config.py](clews_og_bridge/config.py) → mapping rules 
- [models.py](clews_og_bridge/models.py) → schema definitions

## Development Approach & Evolution

This project was not built in one step. It evolved through multiple iterations, each addressing a specific limitation.

### Phase 1 — Basic Pipeline 

Initial version: 
- read CLEWS outputs 
- mapped directly to OG-Core inputs 

Issues identified: 
- implicit assumptions 
- no validation 
- incorrect aggregation logic

### Phase 1.5 — Semantic Mapping Layer 

Improvements: 
- introduced technology → sector mapping 
- added elasticity-based transformations 
- replaced implicit logic with explicit rules 

Key realization: 
> Mapping is not mechanical — it is economic interpretation.

### Phase 2 — OG-Core Compatibility 

Improvements: 
- introduced sector → industry mapping 
- enforced dimensionless TFP (Z) 
- normalized production weights 

Added: 
- strict validation constraints 
- parameter shape enforcement

### Phase 2.6 — Integration Hardening 

Key upgrades: 
- explicit economic interpretation of parameters 
- mapping trace metadata 
- strict schema validation 
- baseline normalization for stability 

Focus: 
> prevent silent failure and invalid model behavior

### Phase 3 — Architecture Refactor 

Major redesign: 
- introduced modular transformer architecture 
- separated configuration from logic 
- isolated economic transformations 

Result: 
- extensible system 
- testable components 
- maintainable structure

## Example Mapping

Total Factor Productivity (Z) is derived from cost signals: 

Z = (C_base / C_current)^α 

Where: 
- C_base → baseline cost 
- C_current → current cost 
- α → elasticity parameter 

Interpretation: 
Lower costs → interpreted as higher effective productivity (under the chosen elasticity assumption)

## Example Output

Generated OG-Core parameter payload (simplified): 

```json 
{ 
  "parameters": { 
    "Z": { 
      "value": { 
        "utilities": { 
          "2020": 1.0, 
          "2021": 0.87 
        } 
      }, 
      "units": "dimensionless", 
      "og_core_meaning": "Total Factor Productivity (proxy from cost signals)" 
    } 
  }, 
  "mapping_trace": { 
    "Z": { 
      "source_variable": "total_discounted_cost", 
      "transformation": "Z = (C_base / C_current)^alpha", 
      "aggregation": "sector-level sum", 
      "elasticity": 0.5 
    } 
  } 
} 
```

This trace makes every transformation: 
- **explicit** 
- **auditable** 
- **reproducible** 

---

## Validation Strategy

The system enforces validation at multiple levels: 

- Structural → schema + shape 
- Numeric → bounds (Z > 0, weights sum to 1) 
- Economic → consistency checks 

Invalid data is rejected early to prevent: 
- incorrect model runs 
- silent failures

## Testing

The system includes: 

- unit tests (transformers) 
- integration tests (pipeline) 
- compatibility tests (OG-Core) 

Example: 
`pytest -v`
Tests cover:
- transformation correctness (unit level)
- pipeline integrity (integration level)
- OG-Core compatibility (contract level)

## Design Principles

- Explicit over implicit 
- Validation before execution 
- Config-driven mappings 
- Reproducibility by design 
- Separation of concerns

## Extending the System 

New mappings can be added without modifying core logic. 

Steps: 
1. Define mapping rules in `mapping.yaml` 
2. Implement a transformer in `transformers/` 
3. Register it in the mapper layer 

This allows: 
- adding new economic variables 
- experimenting with alternative mappings 
- adapting to different country models 

The architecture is intentionally designed to support extension without breaking existing behavior. 

This avoids coupling new features to existing logic, reducing regression risk.

## Current Limitations

- Reverse ETL (OG-Core → CLEWS) not yet implemented 
- Limited to selected CLEWS variables 
- Assumes predefined sector mappings 

These are planned for future extensions.

## Future Work

- bidirectional coupling (reverse ETL) 
- iterative convergence module 
- scenario comparison tools 
- integration with MUIOGO runtime

## Usage

```bash 
python -m clews_og_bridge.cli run --input-dir tests/data --mapping-file configs/mapping.yaml --output-file output.json --scenario "test" --run-id "001"
```

## Key Insight 

The hardest part of this project was not engineering. 

It was deciding what the numbers *mean*. 

At multiple points, simple transformations “worked” technically, but produced economically meaningless results. 

That realization shaped the final system: 
- every transformation is explicit 
- every assumption is traceable 
- every output is validated 

This is what turns a pipeline into a model integration system. 


This becomes especially important in multi-sector policy analysis, where errors in one model propagate across the entire system.
