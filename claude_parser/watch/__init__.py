"""Claude Parser SDK - Watch Domain.

Provides file watching for real-time JSONL monitoring.
95% use case: One line starts watching.

Sync Example:
    from claude_parser.watch import watch

    def on_new(conv, new_messages):
        print(f"Got {len(new_messages)} new messages")

    watch("session.jsonl", on_new)  # Blocks, monitors forever

Async Example:
    from claude_parser.watch import watch_async

    async for conv, new_messages in watch_async("session.jsonl"):
        print(f"Got {len(new_messages)} new messages")
"""

from .async_watcher import watch_async
from .sse_helpers import create_sse_stream, stream_for_sse
from .watcher import watch

__all__ = [
    "watch",
    "watch_async",
    "stream_for_sse",
    "create_sse_stream",
]

# Version
__version__ = "2.0.0"
