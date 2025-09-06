"""
Data processing infrastructure.

Centralized framework dependencies - only place that imports polars/msgspec directly.
"""

from .polars_processor import create_data_processor, PolarsDataProcessor

__all__ = [
    "create_data_processor",
    "PolarsDataProcessor",
]
