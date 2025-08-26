"""DDD Composition Root - Centralized dependency container.

Research-backed approach using python-dependency-injector to:
- Eliminate DRY violations in dependency injection
- Centralize all imports in one place
- Enable easy test overrides without manual patching
- Enforce DDD boundaries and architectural patterns

95/5: Uses dependency-injector library for all wiring.
DDD: Composition root pattern for clean architecture.
SOLID: Single place for dependency configuration.
"""


from dependency_injector import containers, providers

# Analytics components
from .analytics.analyzer import ConversationAnalytics
from .analytics.statistics import MessageStatisticsCalculator
from .analytics.time_analyzer import TimeAnalyzer
from .analytics.tool_analyzer import ToolUsageAnalyzer

# Application services
from .application.conversation_service import ConversationService
from .domain.services.navigation import NavigationService

# Domain services
from .domain.services.session_analyzer import SessionAnalyzer
from .domain.services.token_analyzer import TokenAnalyzer

# Domain imports - all Value Objects centralized here
from .domain.value_objects.ids import AgentId, MessageUuid, SessionId
from .domain.value_objects.token_service import TokenCount, TokenPricing, TokenService

# Infrastructure
from .infrastructure.message_repository import MessageRepository


class Container(containers.DeclarativeContainer):
    """DDD Container - Single source of truth for all dependencies.

    Research pattern: Centralized registration eliminates missing imports
    and DRY violations across the codebase.
    """

    # Configuration
    wiring_config = containers.WiringConfiguration(
        modules=[
            "claude_parser.analytics",
            "claude_parser.application",
            "claude_parser.domain.services",
        ]
    )

    # Value Objects - Domain primitives
    session_id_factory = providers.Factory(SessionId)
    message_uuid_factory = providers.Factory(MessageUuid)
    agent_id_factory = providers.Factory(AgentId)
    token_count_factory = providers.Factory(TokenCount, count=0)

    # Token service with pricing configuration
    token_pricing = providers.Singleton(TokenPricing)
    token_service = providers.Singleton(TokenService, pricing=token_pricing)

    # Infrastructure layer
    message_repository = providers.Factory(MessageRepository)

    # Domain services - Core business logic
    session_analyzer = providers.Factory(SessionAnalyzer)

    navigation_service = providers.Factory(NavigationService)

    token_analyzer = providers.Factory(TokenAnalyzer, token_service=token_service)

    # Analytics - Focused analyzers following SRP
    message_statistics_calculator = providers.Factory(MessageStatisticsCalculator)
    time_analyzer = providers.Factory(TimeAnalyzer)
    tool_analyzer = providers.Factory(ToolUsageAnalyzer)

    # Analytics orchestrator
    conversation_analytics = providers.Factory(
        ConversationAnalytics, token_service=token_service
    )

    # Application services
    conversation_service = providers.Factory(
        ConversationService,
        repository=message_repository,
        session_analyzer=session_analyzer,
    )


# Global container instance
container = Container()


def bootstrap_production() -> Container:
    """Bootstrap production dependencies.

    Returns:
        Configured container for production use
    """
    container.wire(modules=container.wiring_config.modules)
    return container


def bootstrap_testing() -> Container:
    """Bootstrap testing dependencies with overrides.

    Research pattern: Separate test bootstrapper prevents
    DRY violations in test setup.

    Returns:
        Container configured for testing
    """
    test_container = Container()

    # Test-specific overrides can be added here
    # Example: test_container.token_service.override(providers.Factory(MockTokenService))

    test_container.wire(modules=test_container.wiring_config.modules)
    return test_container


# Auto-wire on import
container.wire(modules=container.wiring_config.modules)


__all__ = [
    "Container",
    "container",
    "bootstrap_production",
    "bootstrap_testing",
]
