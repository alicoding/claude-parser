"""
Feature data definitions - Part 1.

SOLID: Single Responsibility - Parser and Hooks features
DRY: Reusable feature definitions
"""

from .models import Feature, FeatureCategory, FeatureStatus


def get_parser_features():
    """Get parser domain features."""
    return [
        Feature(
            name="load",
            category=FeatureCategory.PARSER,
            status=FeatureStatus.COMPLETE,
            description="Load JSONL conversations",
            api_method="load(file_path: str) -> Conversation",
            version_added="1.0.0",
            tests_passing=15,
            tests_total=15,
            coverage_percent=100.0,
        ),
        Feature(
            name="Conversation",
            category=FeatureCategory.PARSER,
            status=FeatureStatus.COMPLETE,
            description="Main conversation aggregate root",
            api_method="Conversation(messages, metadata)",
            version_added="1.0.0",
            tests_passing=20,
            tests_total=20,
            coverage_percent=100.0,
        ),
    ]


def get_hooks_features():
    """Get hooks domain features."""
    return [
        Feature(
            name="hook_input",
            category=FeatureCategory.HOOKS,
            status=FeatureStatus.COMPLETE,
            description="Parse hook JSON from stdin",
            api_method="hook_input() -> HookData",
            version_added="2.0.0",
            tests_passing=11,
            tests_total=11,
            coverage_percent=100.0,
        ),
        Feature(
            name="exit_success",
            category=FeatureCategory.HOOKS,
            status=FeatureStatus.COMPLETE,
            description="Exit with success status",
            api_method="exit_success(message: str = '') -> NoReturn",
            version_added="2.0.0",
            tests_passing=10,
            tests_total=10,
            coverage_percent=100.0,
        ),
        Feature(
            name="exit_block",
            category=FeatureCategory.HOOKS,
            status=FeatureStatus.COMPLETE,
            description="Exit with blocking status",
            api_method="exit_block(reason: str) -> NoReturn",
            version_added="2.0.0",
            tests_passing=10,
            tests_total=10,
            coverage_percent=100.0,
        ),
        Feature(
            name="exit_error",
            category=FeatureCategory.HOOKS,
            status=FeatureStatus.COMPLETE,
            description="Exit with error status",
            api_method="exit_error(message: str) -> NoReturn",
            version_added="2.0.0",
            tests_passing=10,
            tests_total=10,
            coverage_percent=100.0,
        ),
    ]
