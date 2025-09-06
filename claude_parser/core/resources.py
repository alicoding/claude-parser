"""
ResourceManager - Centralized framework resources.

95/5 + Centralized Resources pattern:
- All framework dependencies centralized here
- Micro-components get resources via injection
- Zero resource duplication across the system
"""

from pathlib import Path
from typing import Callable, Any
import polars as pl
import tiktoken


class ResourceManager:
    """Centralized resource manager for all framework dependencies."""

    def __init__(self):
        """Initialize with lazy-loaded framework resources."""
        self._token_encoder = None
        self._data_engine = pl
        self._file_reader = pl.read_ndjson

    def get_token_encoder(self) -> tiktoken.Encoding:
        """Get tiktoken encoder (cached singleton)."""
        if self._token_encoder is None:
            self._token_encoder = tiktoken.get_encoding("cl100k_base")
        return self._token_encoder

    def get_data_engine(self) -> Any:
        """Get polars engine for data processing."""
        return self._data_engine

    def get_file_reader(self) -> Callable[[str], pl.DataFrame]:
        """Get polars JSONL file reader."""
        return self._file_reader


# Global singleton instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get global ResourceManager singleton."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
