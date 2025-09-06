"""
Timeline Visualizer - TRUE 95/5 Rich Framework Implementation.

Creates git-like conversation timelines using Rich Tree widget.
"""

from typing import List, Optional
from rich.tree import Tree
from rich.console import Console

from ..entities.conversation import Conversation
# from ...analytics.analyzer import ToolUsageAnalyzer  # TODO: Fix circular import
from .session_analyzer import SessionAnalyzer


class TimelineVisualizer:
    """TRUE 95/5 timeline visualization using Rich framework."""

    def __init__(self):
        """Initialize with Rich console."""
        self.console = Console()

    def create_conversation_timeline(self, conversation: Conversation) -> str:
        """Rich framework: Create git-like conversation timeline."""
        tree = Tree("🗣️ [bold blue]Conversation Timeline[/bold blue]")

        # SDK: Use existing accessors for clean message access
        all_events = []

        # Add user messages
        for msg in conversation.user_messages:
            if msg.parsed_timestamp:
                all_events.append({
                    'timestamp': msg.parsed_timestamp,
                    'type': 'user',
                    'content': msg.text_content[:100] + "..." if len(msg.text_content) > 100 else msg.text_content,
                    'uuid': msg.uuid
                })

        # Add assistant messages
        for msg in conversation.assistant_messages:
            if msg.parsed_timestamp:
                all_events.append({
                    'timestamp': msg.parsed_timestamp,
                    'type': 'assistant',
                    'content': msg.text_content[:100] + "..." if len(msg.text_content) > 100 else msg.text_content,
                    'uuid': msg.uuid
                })

        # Add tool events
        for tool_use in conversation.tool_uses:
            if hasattr(tool_use, 'timestamp') and tool_use.timestamp:
                tool_name = getattr(tool_use, 'tool_name', getattr(tool_use, 'name', 'unknown'))
                all_events.append({
                    'timestamp': tool_use.timestamp,
                    'type': 'tool',
                    'content': tool_name,
                    'uuid': getattr(tool_use, 'uuid', 'unknown')
                })

        # Sort chronologically
        all_events.sort(key=lambda x: x['timestamp'])

        # Build Rich tree
        for event in all_events[-20:]:  # Show last 20 events
            if event['type'] == 'user':
                tree.add(f"👤 [bold green]User:[/bold green] {event['content']}")
            elif event['type'] == 'assistant':
                tree.add(f"🤖 [bold cyan]Assistant:[/bold cyan] {event['content']}")
            elif event['type'] == 'tool':
                tree.add(f"  └─ 🔧 [yellow]{event['content']}[/yellow]")

        # Render to string using Rich
        with self.console.capture() as capture:
            self.console.print(tree)
        return capture.get()

    def create_checkpoint_view(self, conversation: Conversation, since_timestamp: str) -> str:
        """Rich framework: Show timeline since specific timestamp (checkpoint view)."""
        tree = Tree(f"📊 [bold blue]Changes Since Checkpoint[/bold blue]")

        # SDK: Use existing accessors instead of manual type checking
        checkpoint_events = []

        # Filter user messages by timestamp
        for msg in conversation.user_messages:
            if msg.parsed_timestamp and str(msg.parsed_timestamp) >= since_timestamp:
                checkpoint_events.append({
                    'timestamp': msg.parsed_timestamp,
                    'type': 'user',
                    'content': msg.text_content[:80] + "..." if len(msg.text_content) > 80 else msg.text_content
                })

        # Filter assistant messages by timestamp
        for msg in conversation.assistant_messages:
            if msg.parsed_timestamp and str(msg.parsed_timestamp) >= since_timestamp:
                checkpoint_events.append({
                    'timestamp': msg.parsed_timestamp,
                    'type': 'assistant',
                    'content': msg.text_content[:80] + "..." if len(msg.text_content) > 80 else msg.text_content
                })

        # Filter tool uses by timestamp
        for tool_use in conversation.tool_uses:
            if hasattr(tool_use, 'timestamp') and tool_use.timestamp and str(tool_use.timestamp) >= since_timestamp:
                tool_name = getattr(tool_use, 'tool_name', getattr(tool_use, 'name', 'unknown'))
                checkpoint_events.append({
                    'timestamp': tool_use.timestamp,
                    'type': 'tool',
                    'content': tool_name
                })

        # Sort chronologically
        checkpoint_events.sort(key=lambda x: x['timestamp'])

        if not checkpoint_events:
            tree.add("✨ [dim]No changes since checkpoint[/dim]")
        else:
            for event in checkpoint_events:
                if event['type'] == 'user':
                    tree.add(f"👤 [bold green]User:[/bold green] {event['content']}")
                elif event['type'] == 'assistant':
                    tree.add(f"🤖 [bold cyan]Assistant:[/bold cyan] {event['content']}")
                elif event['type'] == 'tool':
                    tree.add(f"  └─ 🔧 [yellow]{event['content']}[/yellow]")

        # Render to string
        with self.console.capture() as capture:
            self.console.print(tree)
        return capture.get()

    def create_session_timeline(self, conversations: List[Conversation]) -> str:
        """Rich framework: Multi-session timeline view."""
        tree = Tree("🔀 [bold blue]Multi-Session Timeline[/bold blue]")

        for i, conv in enumerate(conversations[:5]):  # Show first 5 sessions
            session_id = conv.session_id or f"session-{i}"
            session_node = tree.add(f"📋 [bold magenta]Session {session_id[:8]}[/bold magenta]")

            # Add session stats using existing analytics
            user_count = len(list(conv.user_messages))
            assistant_count = len(list(conv.assistant_messages))
            tool_count = len(list(conv.tool_uses))

            session_node.add(f"👤 {user_count} user messages")
            session_node.add(f"🤖 {assistant_count} assistant messages")
            session_node.add(f"🔧 {tool_count} tool operations")

        # Render to string
        with self.console.capture() as capture:
            self.console.print(tree)
        return capture.get()
