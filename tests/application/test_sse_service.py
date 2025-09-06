"""
Application Services Domain: SSE streaming

Tests 95% use case streaming services - interface only.
"""

from claude_parser.application.sse_service import (
    StreamingService, StreamFormat, create_sse_stream, create_sse_stream_with_heartbeat
)
from ..framework import EnforcedTestBase


class TestSSEService(EnforcedTestBase):
    """Test SSE service features - streaming interface."""

    def test_streaming_service_exists(self):
        """Interface: StreamingService class exists."""
        assert callable(StreamingService)
        service = StreamingService()
        assert hasattr(service, 'stream_messages')

    def test_stream_formats_enum(self):
        """Interface: StreamFormat enum has expected values."""
        assert hasattr(StreamFormat, 'JSON')
        assert hasattr(StreamFormat, 'SSE')
        assert hasattr(StreamFormat, 'NDJSON')
        assert hasattr(StreamFormat, 'RAW')

    def test_create_sse_stream_function(self):
        """Interface: create_sse_stream function exists."""
        assert callable(create_sse_stream)

        from inspect import signature, isasyncgenfunction
        assert isasyncgenfunction(create_sse_stream)

        sig = signature(create_sse_stream)
        assert 'file_path' in sig.parameters
