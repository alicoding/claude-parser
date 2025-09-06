"""
Polars extension - 95/5 framework extension for conversation analysis.

95%: Polars does ALL the heavy lifting
5%: Simple configuration to make it work with our data
"""

import polars as pl
from typing import List, Dict, Any
from ..core.resources import ResourceManager


class ConversationDataFrame:
    """Micro-component: Extend Polars for conversation data (15 LOC)."""

    def __init__(self, resources: ResourceManager):
        self.resources = resources

    def from_messages(self, messages: List[Dict]) -> pl.DataFrame:
        """Convert messages to Polars DataFrame - simplified structure."""
        # Simplify messages for Polars (framework limitation with complex nested data)
        simplified = []
        for msg in messages:
            simplified.append({
                'type': msg.get('type', 'unknown'),
                'content': str(msg.get('content', '')),
                'timestamp': msg.get('timestamp', ''),
                'uuid': msg.get('uuid', ''),
                'session_id': msg.get('session_id', '')
            })
        return pl.DataFrame(simplified)

    def analyze_tokens(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Token analysis using pure Polars - framework does 95% of work."""
        return {
            'total_messages': df.height,
            'user_messages': df.filter(pl.col('type').str.contains('user')).height,
            'assistant_messages': df.filter(pl.col('type').str.contains('assistant')).height,
            'avg_length': df.select(pl.col('content').str.len_chars().mean()).item(),
        }

    def time_analysis(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Time analysis using pure Polars - framework handles all complexity."""
        return {
            'hourly_dist': df.with_columns(
                pl.col('timestamp').str.strptime(pl.Datetime).dt.hour().alias('hour')
            ).group_by('hour').count().to_dict(as_series=False),
            'duration_minutes': (
                df.select(pl.col('timestamp').str.strptime(pl.Datetime)).max().item() -
                df.select(pl.col('timestamp').str.strptime(pl.Datetime)).min().item()
            ).total_seconds() / 60 if df.height > 1 else 0
        }
