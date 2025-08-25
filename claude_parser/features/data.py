"""
Feature data aggregator for Claude Parser SDK.

SOLID: Single Responsibility - Only aggregation
DRY: Imports from split data files
"""

from toolz import concat

from .feature_data import get_parser_features, get_hooks_features
from .feature_data2 import (
    get_todo_features,
    get_watch_transport_features,
    get_filter_navigation_features,
    get_planned_features
)
from .registry import FeatureRegistry


def get_current_features():
    """Get all current feature definitions."""
    return list(concat([
        get_parser_features(),
        get_hooks_features(),
        get_todo_features(),
        get_watch_transport_features(),
        get_filter_navigation_features(),
        get_planned_features()
    ]))


def get_registry() -> FeatureRegistry:
    """Get the current feature registry."""
    return FeatureRegistry(
        version="2.0.3",
        features=get_current_features()
    )