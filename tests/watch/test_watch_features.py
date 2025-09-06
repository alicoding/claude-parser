"""
Watch Domain: Real-time JSONL monitoring

Tests 95% use case watch functions - interface only.
"""

import asyncio
from pathlib import Path
from claude_parser.watch import watch, watch_async, create_sse_stream, stream_for_sse
from ..framework import EnforcedTestBase


class TestWatchFeatures(EnforcedTestBase):
    """Test watch features - real-time monitoring."""

    def test_watch_async_interface_contract(self):
        """Interface: watch_async() accepts path, returns async generator."""
        from claude_parser.watch import watch_async
        from inspect import isasyncgenfunction

        # Interface contract
        assert callable(watch_async)
        assert isasyncgenfunction(watch_async)

    def test_watch_sync_interface_contract(self):
        """Interface: watch() accepts path and callback."""
        from claude_parser.watch import watch
        from inspect import signature

        # Interface contract
        assert callable(watch)
        sig = signature(watch)
        assert 'file_path' in sig.parameters
        assert 'callback' in sig.parameters

    def test_sse_helpers_interface_contract(self):
        """Interface: SSE helpers accept path, return generators."""
        from claude_parser.watch import create_sse_stream, stream_for_sse
        from inspect import isasyncgenfunction

        # Interface contracts
        assert callable(create_sse_stream)
        assert isasyncgenfunction(create_sse_stream)
        assert callable(stream_for_sse)
        assert isasyncgenfunction(stream_for_sse)
