"""
FileLoader micro-component - JSONL file loading.

95/5 principle: Use standard library for JSONL, framework for processing.
Size: ~18 LOC (LLM-readable in single context)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from ..core.resources import ResourceManager


class FileLoader:
    """Micro-component: Load JSONL files using standard library."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def load(self, file_path: str | Path) -> List[Dict[str, Any]]:
        """Load JSONL file - standard library handles complex JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
