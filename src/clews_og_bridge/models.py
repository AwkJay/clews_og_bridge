from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict


class Metadata(BaseModel):
    run_id: str
    schema_version: str = "1.2.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    scenario: str
    country: Optional[str] = None
    pipeline_version: str = "1.0.0"


class ClewsOutputs(BaseModel):
    """Normalized CLEWS variables by technology and year."""
    years: List[int]
    technologies: List[str]
    # mapping: variable_name -> technology -> year -> value
    data: Dict[str, Dict[str, Dict[str, float]]]


class ParameterDimensions(BaseModel):
    """Explicit dimension names for the parameter (e.g., ['time', 'industry'])."""
    names: List[str]
    industry_indices: Optional[Dict[str, int]] = None


class MappingTraceEntry(BaseModel):
    source_variable: str
    target_parameter: str
    economic_interpretation: str
    injection_location: str # e.g. "update_specifications -> production function"
    parameter_role: str # e.g. "scaling factor for sectoral TFP"
    transformation_type: str
    formula: str
    input_unit: str
    aggregation_rule: str
    baseline_reference: Optional[str] = None
    elasticity_used: Optional[float] = None


class OgParameterValue(BaseModel):
    """Explicit shape and metadata for an OG-Core parameter injection."""
    value: Dict[str, Dict[str, float]] # industry -> year -> float
    dimensions: ParameterDimensions
    units: str
    og_core_meaning: str


class OgParameters(BaseModel):
    """The revision dictionary structured for OG-Core update_specifications()."""
    # mapping: parameter_name -> OgParameterValue
    parameters: Dict[str, OgParameterValue]
    # Structured mapping trace for auditing
    mapping_trace: Dict[str, MappingTraceEntry]


class ExchangeModel(BaseModel):
    metadata: Metadata
    clews_outputs: ClewsOutputs
    og_parameters: OgParameters

    model_config = ConfigDict(extra="forbid")
