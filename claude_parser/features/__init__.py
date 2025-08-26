"""
Feature tracking system for Claude Parser SDK.

SOLID: Separated into single responsibilities
- models.py: Data models only
- registry.py: Registry operations only
- data.py: Feature data only
"""

from .data import get_current_features, get_registry
from .models import Feature, FeatureCategory, FeatureStatus
from .registry import FeatureRegistry

__all__ = [
    "Feature",
    "FeatureStatus",
    "FeatureCategory",
    "FeatureRegistry",
    "get_current_features",
    "get_registry",
]
