"""
Time analysis for conversations - SOLID Single Responsibility.

Focused solely on temporal patterns and distributions.
"""

from typing import Dict, List, Optional
from collections import defaultdict
import pendulum

from ..domain.entities.conversation import Conversation


class TimeAnalyzer:
    """Analyzes temporal patterns in conversations.

    SOLID: Single Responsibility - Only time-based analysis
    95/5: Uses pendulum for date/time operations
    """

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.conversation = conversation

    def get_hourly_distribution(self) -> Dict[int, int]:
        """Get message distribution by hour of day.

        Returns:
            Dictionary mapping hour (0-23) to message count
        """
        distribution = defaultdict(int)

        for msg in self.conversation.messages:
            if msg.parsed_timestamp:
                hour = msg.parsed_timestamp.hour
                distribution[hour] += 1

        return dict(distribution)

    def get_daily_distribution(self) -> Dict[str, int]:
        """Get message distribution by date.

        Returns:
            Dictionary mapping date string (YYYY-MM-DD) to message count
        """
        distribution = defaultdict(int)

        for msg in self.conversation.messages:
            if msg.parsed_timestamp:
                date_str = msg.parsed_timestamp.format('YYYY-MM-DD')
                distribution[date_str] += 1

        return dict(distribution)

    def calculate_duration_minutes(self) -> float:
        """Calculate total conversation duration in minutes.

        Returns:
            Duration in minutes from first to last message
        """
        timestamps = [
            msg.parsed_timestamp
            for msg in self.conversation.messages
            if msg.parsed_timestamp
        ]

        if len(timestamps) < 2:
            return 0.0

        # Sort timestamps
        timestamps.sort()
        first, last = timestamps[0], timestamps[-1]

        # Calculate duration
        duration = last - first
        return duration.total_seconds() / 60.0

    def get_response_times(self) -> List[float]:
        """Calculate response times between user and assistant messages.

        Returns:
            List of response times in seconds
        """
        response_times = []
        last_user_time = None

        for msg in self.conversation.messages:
            if not msg.parsed_timestamp:
                continue

            msg_type = str(msg.type).lower()

            if 'user' in msg_type:
                last_user_time = msg.parsed_timestamp
            elif 'assistant' in msg_type and last_user_time:
                # Calculate response time
                response_time = msg.parsed_timestamp - last_user_time
                response_times.append(response_time.total_seconds())
                last_user_time = None  # Reset for next pair

        return response_times

    def get_peak_hours(self, limit: int = 3) -> List[int]:
        """Get the most active hours of the day.

        Args:
            limit: Number of top hours to return

        Returns:
            List of hours (0-23) sorted by activity
        """
        hourly = self.get_hourly_distribution()

        # Sort by message count, descending
        sorted_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)

        return [hour for hour, count in sorted_hours[:limit]]


__all__ = ["TimeAnalyzer"]
