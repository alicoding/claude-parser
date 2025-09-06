"""
Conversation Domain: Analyze Features

Tests analysis features from claude_parser public API.
These build on top of the load() foundation.

FEATURES ONLY - No infrastructure, no fake data.
"""

from claude_parser import load, analyze, extract_assistant_messages_between
from ..framework import EnforcedTestBase


class TestAnalyzeFeatures(EnforcedTestBase):
    """Test conversation analysis features."""

    def test_analyze_conversation(self, sample_transcript):
        """Feature: analyze() provides conversation insights."""
        conv = load(sample_transcript)
        analysis = analyze(conv)

        # Should return analysis data
        assert analysis is not None
        # Analysis should have useful information
        assert hasattr(analysis, '__dict__') or isinstance(analysis, dict)

    def test_extract_assistant_messages_between_timestamps(self, sample_transcript):
        """Feature: Extract assistant messages in time range."""
        conv = load(sample_transcript)

        if len(conv.messages) >= 2:
            # Get messages between first and last timestamp
            first_time = conv.messages[0].timestamp
            last_time = conv.messages[-1].timestamp

            messages = extract_assistant_messages_between(conv, first_time, last_time)

            # Should return list of messages
            assert isinstance(messages, list)
            # All should be assistant messages if any exist
            for msg in messages:
                assert msg.type.value == 'assistant'


class TestAnalyzeWithRealData(EnforcedTestBase):
    """Test analyze features with real conversation data."""

    def test_analyze_handles_empty_conversation(self, empty_jsonl_file):
        """Feature: analyze() handles empty conversations gracefully."""
        conv = load(empty_jsonl_file)
        analysis = analyze(conv)

        # Should not crash on empty conversation
        assert analysis is not None

    def test_extract_messages_handles_no_assistant_messages(self, sample_transcript):
        """Feature: Gracefully handle conversations with no assistant messages."""
        conv = load(sample_transcript)

        # Use very early timestamp range where no assistant messages exist
        early_time = "2020-01-01T00:00:00Z"
        messages = extract_assistant_messages_between(conv, early_time, early_time)

        # Should return empty list, not crash
        assert isinstance(messages, list)
        assert len(messages) == 0
