"""
Application-wide constants.

SOLID: Single source of truth for constants.
DRY: Eliminate magic strings/numbers.
95/5: Constants are part of the 5% glue code.
"""

from enum import Enum


# File patterns
JSONL_EXTENSION = ".jsonl"
JSONL_PATTERN = "*.jsonl"

# Size limits
MAX_LINE_LENGTH = 10000  # Maximum line length in JSONL files
DEFAULT_BATCH_SIZE = 1000  # Default batch size for processing

# Performance thresholds
MAX_PROCESSING_TIME = 10.0  # Maximum seconds for processing
MIN_PERFORMANCE_RATIO = 0.8  # Minimum performance ratio

# Default values
DEFAULT_MODEL = "claude-3-opus-20240229"
DEFAULT_ENCODING = "utf-8"

# Session patterns
SESSION_ID_LENGTH = 36  # UUID v4 length with hyphens
SESSION_ID_PATTERN = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"

# Message type strings (for backward compatibility)
USER_MESSAGE_TYPE = "user"
ASSISTANT_MESSAGE_TYPE = "assistant"
TOOL_USE_TYPE = "tool_use"
TOOL_RESULT_TYPE = "tool_result"
SUMMARY_TYPE = "summary"

# Tool names
COMMON_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "LS",
    "Search",
    "WebSearch",
    "WebFetch",
]

# Error messages
ERROR_FILE_NOT_FOUND = "File not found: {}"
ERROR_INVALID_JSON = "Invalid JSON at line {}: {}"
ERROR_MISSING_FIELD = "Missing required field: {}"
ERROR_INVALID_TYPE = "Invalid type: expected {}, got {}"

# Logging prefixes
LOG_PREFIX_INFO = "[INFO]"
LOG_PREFIX_WARNING = "[WARNING]"
LOG_PREFIX_ERROR = "[ERROR]"
LOG_PREFIX_DEBUG = "[DEBUG]"


class ProcessingStatus(Enum):
    """Processing status constants."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class HookEventType(Enum):
    """Hook event type constants."""

    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    STOP = "Stop"
    NOTIFICATION = "Notification"
    SUBAGENT_STOP = "SubagentStop"
    PRE_COMPACT = "PreCompact"
    SESSION_START = "SessionStart"


# Export for convenience
__all__ = [
    # Patterns
    "JSONL_EXTENSION",
    "JSONL_PATTERN",
    # Limits
    "MAX_LINE_LENGTH",
    "DEFAULT_BATCH_SIZE",
    # Performance
    "MAX_PROCESSING_TIME",
    "MIN_PERFORMANCE_RATIO",
    # Defaults
    "DEFAULT_MODEL",
    "DEFAULT_ENCODING",
    # Session
    "SESSION_ID_LENGTH",
    "SESSION_ID_PATTERN",
    # Message types
    "USER_MESSAGE_TYPE",
    "ASSISTANT_MESSAGE_TYPE",
    "TOOL_USE_TYPE",
    "TOOL_RESULT_TYPE",
    "SUMMARY_TYPE",
    # Tools
    "COMMON_TOOLS",
    # Errors
    "ERROR_FILE_NOT_FOUND",
    "ERROR_INVALID_JSON",
    "ERROR_MISSING_FIELD",
    "ERROR_INVALID_TYPE",
    # Logging
    "LOG_PREFIX_INFO",
    "LOG_PREFIX_WARNING",
    "LOG_PREFIX_ERROR",
    "LOG_PREFIX_DEBUG",
    # Enums
    "ProcessingStatus",
    "HookEventType",
]
