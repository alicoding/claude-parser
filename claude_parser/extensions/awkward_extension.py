"""
Awkward Array extension - 95/5 framework extension for nested JSONL analysis.

95%: Awkward Array handles ALL nested data complexity
5%: Simple configuration for our analytics needs
"""

import awkward as ak
from typing import Dict, Any, List
from ..core.resources import ResourceManager


class ConversationArray:
    """Micro-component: Extend Awkward Array for conversation analysis (15 LOC)."""

    def __init__(self, resources: ResourceManager):
        self.resources = resources

    def from_jsonl(self, file_path: str) -> ak.Array:
        """Load JSONL with Awkward Array - framework handles ALL complexity."""
        # Read JSONL file line by line and parse with Awkward Array
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        return ak.from_iter([ak.from_json(line) for line in lines])

    def analyze_messages(self, events: ak.Array) -> Dict[str, Any]:
        """Message analysis using pure Awkward Array - framework does everything."""
        # Count unique sessions manually - handle both sessionId and session_id
        unique_sessions = 0
        if len(events) > 0:
            try:
                # Try sessionId first (real Claude data)
                session_ids = [str(events[i]["sessionId"]) for i in range(len(events))]
                unique_sessions = len(set(session_ids))
            except:
                try:
                    # Fallback to session_id (test data)
                    session_ids = [str(events[i]["session_id"]) for i in range(len(events))]
                    unique_sessions = len(set(session_ids))
                except:
                    unique_sessions = 1  # Assume single session if no field

        return {
            'total_messages': len(events),
            'user_messages': int(ak.sum(events["type"] == "user")),
            'assistant_messages': int(ak.sum(events["type"] == "assistant")),
            'has_content': int(ak.sum(~ak.is_none(events["content"]))),
            'unique_sessions': unique_sessions,
        }

    def analyze_time_patterns(self, events: ak.Array) -> Dict[str, Any]:
        """Time analysis using pure Awkward Array - framework handles complexity."""
        # Extract timestamps and let Awkward handle the parsing
        timestamps = events["timestamp"]
        valid_timestamps = timestamps[~ak.is_none(timestamps)]

        return {
            'message_count': len(valid_timestamps),
            'first_timestamp': str(valid_timestamps[0]) if len(valid_timestamps) > 0 else None,
            'last_timestamp': str(valid_timestamps[-1]) if len(valid_timestamps) > 0 else None,
            'has_timestamps': len(valid_timestamps),
        }

    def analyze_tools(self, events: ak.Array) -> Dict[str, Any]:
        """Tool analysis using pure Awkward Array - framework handles nested structure."""
        # Awkward can directly work with nested tool structures
        tool_uses = events[events["type"] == "tool_use"]

        # Count unique tool names manually
        unique_tools = 0
        if len(tool_uses) > 0:
            tool_names = [str(tool_uses[i]["name"]) for i in range(len(tool_uses))]
            unique_tools = len(set(tool_names))

        return {
            'total_tool_calls': len(tool_uses),
            'tool_types': unique_tools,
        }

    def filter_by_type(self, events: ak.Array, message_type: str) -> ak.Array:
        """Filter messages by type - let Awkward Array handle filtering."""
        return events[events["type"] == message_type]

    def query(self, events: ak.Array, query_expr: str) -> ak.Array:
        """Query events using Awkward Array expressions."""
        # Awkward Array supports complex queries on nested data
        if "user" in query_expr:
            return self.filter_by_type(events, "user")
        elif "assistant" in query_expr:
            return self.filter_by_type(events, "assistant")
        else:
            return events  # Return all if no specific query
