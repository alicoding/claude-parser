"""
Claude Parser - Clean 95/5 + Framework Extensions Architecture.

95% frameworks do the heavy lifting, 5% glue code.
Zero tech debt, zero backward compatibility layers.
"""

# Pure Framework-Based API
from .api.factory import (
    analyze_conversation as analyze,
    load_conversation as load,
    load_many_conversations as load_many,
    watch_conversation as watch_async,
    create_timeline,
    discover_transcripts as find_current_transcript,
)

# Framework Extensions (for advanced use)
from .extensions.polars_extension import ConversationDataFrame
from .extensions.typer_extension import app as cli

# Simple Models (data classes only)
from .models import (
    Message,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ContentBlock,
    ToolUseContent,
    ToolResultContent,
    Summary,
)

# Analytics via Framework Extensions
class ConversationAnalytics:
    """Analytics using pure Polars framework."""

    def __init__(self, conversation_data):
        from .core.resources import get_resource_manager
        from .extensions.polars_extension import ConversationDataFrame

        self.resources = get_resource_manager()
        self.df_ext = ConversationDataFrame(self.resources)
        self.data = conversation_data

    def get_statistics(self):
        """Get statistics using Polars framework."""
        import polars as pl
        df = pl.DataFrame(self.data)
        return self.df_ext.analyze_tokens(df)

    def get_time_analysis(self):
        """Get time analysis using Polars framework."""
        import polars as pl
        df = pl.DataFrame(self.data)
        return self.df_ext.time_analysis(df)


class TokenCounter:
    """Token counter using tiktoken framework."""

    def __init__(self):
        from .core.resources import get_resource_manager
        from .components.token_counter import TokenCounter as TokenCounterComponent

        self.resources = get_resource_manager()
        self.counter = TokenCounterComponent(self.resources)

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken framework."""
        return self.counter.count(text)


# Discovery using pathlib framework
def find_transcript_for_cwd(cwd):
    """Find transcript using pathlib framework."""
    return discover_transcripts(cwd)[0] if discover_transcripts(cwd) else None


def find_all_transcripts_for_cwd(cwd):
    """Find all transcripts using pathlib framework."""
    return discover_transcripts(cwd)


# Watch using watchfiles framework
def watch(file_path, callback):
    """Sync watch using asyncio + watchfiles framework."""
    import asyncio

    async def _async_watch():
        async for conversation, new_messages in watch_async(file_path):
            callback(conversation, new_messages)

    asyncio.run(_async_watch())


# SSE using fastapi framework patterns
async def stream_for_sse(file_path, format_message=None):
    """Stream for SSE using frameworks."""
    import json

    if format_message is None:
        def format_message(msg):
            return {
                "type": msg.get("type", "unknown"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", "")
            }

    async for conversation, new_messages in watch_async(file_path):
        for msg in new_messages:
            yield {"data": json.dumps(format_message(msg))}


async def create_sse_stream(file_path):
    """Create SSE stream using frameworks."""
    async for event in stream_for_sse(file_path):
        yield event


# Export all
__all__ = [
    # Main API (95% use case)
    "load",
    "load_many",
    "analyze",
    "watch_async",
    "watch",
    # Discovery
    "find_current_transcript",
    "find_transcript_for_cwd",
    "find_all_transcripts_for_cwd",
    # Analytics
    "ConversationAnalytics",
    "TokenCounter",
    # Models
    "Message",
    "UserMessage",
    "AssistantMessage",
    "SystemMessage",
    "ContentBlock",
    "ToolUseContent",
    "ToolResultContent",
    "Summary",
    # SSE
    "stream_for_sse",
    "create_sse_stream",
    # CLI
    "cli",
]

__version__ = "2.0.0"  # Clean Architecture Version
