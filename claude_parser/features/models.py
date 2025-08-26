"""
Feature models for SDK capability tracking.

SOLID: Single Responsibility - Only data models
DDD: Value Objects - Immutable feature definitions
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FeatureStatus(str, Enum):
    """Feature implementation status."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    PLANNED = "planned"
    NOT_STARTED = "not_started"


class FeatureCategory(str, Enum):
    """Feature categories for organization."""

    PARSER = "parser"
    HOOKS = "hooks"
    WATCH = "watch"
    ANALYTICS = "analytics"
    MEMORY = "memory"
    TRANSPORT = "transport"
    FILTERS = "filters"
    NAVIGATION = "navigation"


class Feature(BaseModel):
    """Individual feature definition."""

    # Core attributes
    name: str = Field(..., description="Feature name")
    category: FeatureCategory = Field(..., description="Category")
    status: FeatureStatus = Field(..., description="Status")

    # Documentation
    description: str = Field(..., description="What it does")
    api_method: Optional[str] = Field(None, description="API signature")

    # Version tracking
    version_added: Optional[str] = Field(None, description="When added")
    version_deprecated: Optional[str] = Field(None, description="When deprecated")
    removal_version: Optional[str] = Field(None, description="When removed")

    # Implementation details
    tests_passing: Optional[int] = Field(None, description="Passing tests")
    tests_total: Optional[int] = Field(None, description="Total tests")
    coverage_percent: Optional[float] = Field(None, description="Coverage %")

    # Dependencies and notes
    depends_on: List[str] = Field(default_factory=list, description="Dependencies")
    migration_guide: Optional[str] = Field(None, description="Migration guide")
    notes: Optional[str] = Field(None, description="Notes")

    model_config = {"json_schema_extra": {"examples": []}}
