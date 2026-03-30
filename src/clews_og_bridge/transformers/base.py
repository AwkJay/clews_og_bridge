from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
from ..config import MappingConfig

class EconomicTransformer(ABC):
    """Base interface for economic mapping transformers."""
    
    @abstractmethod
    def transform(self, df: pd.DataFrame, config: MappingConfig, var_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Transform normalized data into economic parameter format.
        
        Args:
            df: Normalized input DataFrame.
            config: Mapping configuration.
            var_name: Name of the input variable.
            
        Returns:
            A tuple of (mapped_dataframe, trace_metadata).
        """
        pass
