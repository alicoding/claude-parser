"""
Error detection filter.

SOLID: Single Responsibility - Only error detection.
95/5: Using toolz for functional operations.
"""

from typing import List
from toolz import pipe, map as toolz_map, filter as toolz_filter

from ...models import Message


class ErrorFilter:
    """Filter messages containing errors."""
    
    ERROR_KEYWORDS = ('error', 'exception', 'failed', 'failure', 'traceback')
    STACK_TRACE_INDICATORS = ('Traceback', 'File "', 'line ', '    at ', 'Error:')
    
    def matches(self, message: Message) -> bool:
        """Check if message contains error indicators."""
        content = message.text_content.lower()
        
        # Use functional approach instead of any() with generator
        return pipe(
            self.ERROR_KEYWORDS,
            lambda keywords: toolz_map(lambda k: k in content, keywords),
            any
        )
    
    def extract_stack_traces(self, messages: List[Message]) -> List[str]:
        """Extract stack traces from messages using toolz_filter."""
        return pipe(
            messages,
            lambda msgs: toolz_filter(self.has_stack_trace, msgs),
            lambda msgs: toolz_map(lambda m: m.text_content, msgs),
            list
        )
    
    def has_stack_trace(self, message: Message) -> bool:
        """Check if message contains a stack trace."""
        content = message.text_content
        
        return pipe(
            self.STACK_TRACE_INDICATORS,
            lambda indicators: toolz_map(lambda i: i in content, indicators),
            any
        )