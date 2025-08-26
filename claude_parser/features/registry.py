"""
Feature registry operations.

SOLID: Single Responsibility - Only registry operations
95/5: Using toolz for functional operations
"""

from typing import Dict, List

import orjson
import pendulum
from pydantic import BaseModel, Field
from toolz import filter as toolz_filter
from toolz import map as toolz_map
from toolz import pipe

from .models import Feature, FeatureCategory, FeatureStatus


class FeatureRegistry(BaseModel):
    """SDK Feature Registry - Single source of truth for capabilities."""

    sdk_name: str = Field("claude-parser", description="SDK name")
    version: str = Field(..., description="Current SDK version")
    updated: str = Field(
        default_factory=lambda: pendulum.now().isoformat(), description="Last update"
    )
    features: List[Feature] = Field(default_factory=list, description="Features")

    model_config = {"json_schema_extra": {"examples": []}}

    def get_by_status(self, status: FeatureStatus) -> List[Feature]:
        """Get features by status."""
        return list(toolz_filter(lambda f: f.status == status, self.features))

    def get_by_category(self, category: FeatureCategory) -> List[Feature]:
        """Get features by category."""
        return list(toolz_filter(lambda f: f.category == category, self.features))

    def get_complete_features(self) -> List[Feature]:
        """Get all complete features."""
        return self.get_by_status(FeatureStatus.COMPLETE)

    def get_incomplete_features(self) -> List[Feature]:
        """Get all incomplete features."""
        incomplete = [
            FeatureStatus.PARTIAL,
            FeatureStatus.PLANNED,
            FeatureStatus.NOT_STARTED,
        ]
        return list(toolz_filter(lambda f: f.status in incomplete, self.features))

    def get_deprecated_features(self) -> List[Feature]:
        """Get deprecated features."""
        return self.get_by_status(FeatureStatus.DEPRECATED)

    def to_capability_matrix(self) -> Dict[str, Dict[str, str]]:
        """Generate capability matrix for documentation."""
        return pipe(
            list(FeatureCategory),
            lambda cats: toolz_map(
                lambda cat: (
                    cat.value,
                    dict(
                        toolz_map(
                            lambda f: (f.name, f.status.value),
                            self.get_by_category(cat),
                        )
                    ),
                ),
                cats,
            ),
            dict,
        )


def save_registry(registry: FeatureRegistry, path: str = "docs/api/FEATURES.json"):
    """Save registry to JSON file."""
    with open(path, "wb") as f:
        f.write(orjson.dumps(registry.model_dump(), option=orjson.OPT_INDENT_2))


def load_registry(path: str = "docs/api/FEATURES.json") -> FeatureRegistry:
    """Load registry from JSON file."""
    with open(path, "rb") as f:
        data = orjson.loads(f.read())
    return FeatureRegistry(**data)
