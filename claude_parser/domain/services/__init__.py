"""Domain services."""

from .analyzer import ConversationAnalyzer
from .context_window_manager import (
    ContextStatus,
    ContextWindowInfo,
    ContextWindowManager,
)
from .file_navigator import FileNavigator
from .navigation import NavigationService
from .session_analyzer import SessionAnalyzer, SessionStats
from .timeline_service import Timeline
from .claude_code_timeline import ClaudeCodeTimeline

# Alias for backward compatibility and clearer naming in tests
RealClaudeTimeline = ClaudeCodeTimeline

__all__ = [
    "ConversationAnalyzer",
    "NavigationService",
    "ContextWindowManager",
    "ContextWindowInfo",
    "ContextStatus",
    "SessionAnalyzer",
    "SessionStats",
    "Timeline",
    "ClaudeCodeTimeline",
    "RealClaudeTimeline",
    "FileNavigator",
]
