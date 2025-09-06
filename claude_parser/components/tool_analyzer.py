"""
ToolAnalyzer micro-component - Tool usage pattern analysis.

95/5 principle: Simple tool counting logic, framework handles data structures.
Size: ~15 LOC (LLM-readable in single context)
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from ..core.resources import ResourceManager
from ..models import Message
from ..models.content import ToolUseContent


class ToolAnalyzer:
    """Micro-component: Analyze tool usage patterns."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def analyze_tool_usage(self, messages: List[Message]) -> Dict[str, Any]:
        """Analyze tool usage patterns - simple Python logic."""
        tool_counts = defaultdict(int)

        # Extract from conversation.tool_uses if available, or iterate messages
        for msg in messages:
            if hasattr(msg, 'content_blocks'):
                for block in getattr(msg, 'content_blocks', []):
                    if isinstance(block, ToolUseContent):
                        tool_counts[block.name] += 1

        # Sort by usage count
        most_used = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'tool_usage_counts': dict(tool_counts),
            'most_used_tools': most_used,
            'total_tool_calls': sum(tool_counts.values()),
            'unique_tools': len(tool_counts),
        }
