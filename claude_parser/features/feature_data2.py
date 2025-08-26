"""
Feature data definitions - Part 2.

SOLID: Single Responsibility - Other domain features
DRY: Reusable feature definitions
"""

from .models import Feature, FeatureCategory, FeatureStatus


def get_todo_features():
    """Get Todo domain features."""
    return [
        Feature(
            name="TodoManager",
            category=FeatureCategory.NAVIGATION,
            status=FeatureStatus.COMPLETE,
            description="Manage Claude's TodoWrite format with Rich display",
            api_method="TodoManager(session_id, agent_id=None)",
            version_added="3.1.0",
            tests_passing=14,
            tests_total=14,
            coverage_percent=100.0,
            notes="SOLID/DRY/DDD implementation with Rich display",
        ),
        Feature(
            name="TodoSwiper",
            category=FeatureCategory.NAVIGATION,
            status=FeatureStatus.COMPLETE,
            description="Tinder-like navigation through todo history",
            api_method="TodoSwiper.from_transcript(path)",
            version_added="3.1.0",
            tests_passing=3,
            tests_total=3,
            coverage_percent=100.0,
            notes="Timeline integration for todo history",
        ),
        Feature(
            name="TodoParser",
            category=FeatureCategory.PARSER,
            status=FeatureStatus.COMPLETE,
            description="Parse TodoWrite JSON format",
            api_method="TodoParser.parse(data)",
            version_added="3.1.0",
            tests_passing=5,
            tests_total=5,
            coverage_percent=100.0,
            notes="95% orjson library usage",
        ),
    ]


def get_watch_transport_features():
    """Get watch and transport features."""
    return [
        Feature(
            name="watch",
            category=FeatureCategory.WATCH,
            status=FeatureStatus.COMPLETE,
            description="Real-time JSONL file monitoring",
            api_method="watch(file_path, callback, message_types=None)",
            version_added="2.0.0",
            tests_passing=4,
            tests_total=4,
            coverage_percent=100.0,
        ),
        Feature(
            name="SSE Transport",
            category=FeatureCategory.TRANSPORT,
            status=FeatureStatus.COMPLETE,
            description="Server-Sent Events transport layer",
            api_method="createTransport(url, options?)",
            version_added="2.0.3",
            tests_passing=21,
            tests_total=21,
            coverage_percent=100.0,
            notes="TypeScript implementation",
        ),
    ]


def get_filter_navigation_features():
    """Get filter and navigation features."""
    return [
        Feature(
            name="error_filter",
            category=FeatureCategory.FILTERS,
            status=FeatureStatus.COMPLETE,
            description="Filter messages with errors and extract stack traces",
            api_method="ErrorFilter.matches(message) -> bool",
            version_added="2.0.0",
            notes="Stack trace extraction added",
            tests_passing=3,
            tests_total=3,
            coverage_percent=100.0,
        ),
        Feature(
            name="thread_navigation",
            category=FeatureCategory.NAVIGATION,
            status=FeatureStatus.PARTIAL,
            description="Navigate conversation threads",
            api_method="NavigationService.find_thread_messages()",
            version_added="2.0.0",
            notes="NetworkX integration incomplete",
        ),
    ]


def get_planned_features():
    """Get planned features."""
    return [
        Feature(
            name="token_counting",
            category=FeatureCategory.ANALYTICS,
            status=FeatureStatus.COMPLETE,
            description="Count tokens in messages",
            api_method="TokenCounter().count_tokens(text)",
            version_added="2.0.3",
            tests_passing=1,
            tests_total=1,
            coverage_percent=100.0,
            notes="Uses tiktoken for accurate counting, fallback estimation",
        ),
        Feature(
            name="error_patterns",
            category=FeatureCategory.ANALYTICS,
            status=FeatureStatus.PLANNED,
            description="Analyze error patterns",
            api_method="analytics.error_patterns(conversations)",
            depends_on=["pandas", "scipy"],
        ),
        Feature(
            name="mem0_export",
            category=FeatureCategory.MEMORY,
            status=FeatureStatus.PLANNED,
            description="Export to mem0 memory system",
            api_method="conversation.to_mem0()",
            depends_on=["mem0"],
        ),
        Feature(
            name="embeddings",
            category=FeatureCategory.MEMORY,
            status=FeatureStatus.PLANNED,
            description="Generate embeddings for messages",
            api_method="conversation.to_embeddings()",
            depends_on=["sentence-transformers"],
        ),
    ]
