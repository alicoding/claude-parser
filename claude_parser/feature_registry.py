"""
Feature Registry - Backward compatibility.

This file maintains backward compatibility.
The actual implementation is in the features/ package.

SOLID: Single import/export responsibility
"""

from .features import (
    Feature,
    FeatureCategory,
    FeatureRegistry,
    FeatureStatus,
    get_registry,
)
from .features.registry import load_registry, save_registry

# Maintain backward compatibility
CURRENT_REGISTRY = get_registry()

__all__ = [
    "Feature",
    "FeatureStatus",
    "FeatureCategory",
    "FeatureRegistry",
    "get_registry",
    "save_registry",
    "load_registry",
    "CURRENT_REGISTRY",
]
