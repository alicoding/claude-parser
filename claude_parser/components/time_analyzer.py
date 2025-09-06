"""
TimeAnalyzer micro-component - Temporal pattern analysis.

95/5 principle: Simple time calculations, framework handles data structures.
Size: ~20 LOC (LLM-readable in single context)
"""

from typing import List, Dict, Any
from collections import defaultdict
from ..core.resources import ResourceManager
from ..models import Message, UserMessage, AssistantMessage


class TimeAnalyzer:
    """Micro-component: Analyze temporal patterns."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def analyze_time_patterns(self, messages: List[Message]) -> Dict[str, Any]:
        """Analyze time patterns - simple Python logic."""
        from datetime import datetime

        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        response_times = []
        last_user_time = None

        # Parse timestamps that exist
        parsed_messages = []
        for msg in messages:
            if hasattr(msg, 'parsed_timestamp') and msg.parsed_timestamp:
                try:
                    # Handle string timestamps
                    if isinstance(msg.parsed_timestamp, str):
                        # Parse ISO format: 2025-08-31T18:00:14.328Z
                        timestamp_str = msg.parsed_timestamp.replace('Z', '+00:00')
                        parsed_time = datetime.fromisoformat(timestamp_str)
                    else:
                        parsed_time = msg.parsed_timestamp

                    parsed_messages.append((msg, parsed_time))
                except (ValueError, AttributeError):
                    continue

        for msg, parsed_time in parsed_messages:
            # Hour and daily distribution
            hourly_dist[parsed_time.hour] += 1
            daily_dist[parsed_time.strftime("%Y-%m-%d")] += 1

            # Response times between user and assistant
            if isinstance(msg, UserMessage):
                last_user_time = parsed_time
            elif isinstance(msg, AssistantMessage) and last_user_time:
                response_times.append((parsed_time - last_user_time).total_seconds())
                last_user_time = None

        # Calculate duration
        if len(parsed_messages) >= 2:
            first_time = parsed_messages[0][1]
            last_time = parsed_messages[-1][1]
            duration = (last_time - first_time).total_seconds() / 60.0
        else:
            duration = 0.0

        return {
            'hourly_distribution': dict(hourly_dist),
            'daily_distribution': dict(daily_dist),
            'duration_minutes': duration,
            'response_times': response_times,
            'peak_hours': sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3],
        }
