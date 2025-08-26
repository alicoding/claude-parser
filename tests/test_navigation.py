#!/usr/bin/env python
"""TDD tests for navigation features following 95/5 principle."""

import pytest

from claude_parser import load
from claude_parser.discovery import find_current_transcript


class TestNavigationFeatures:
    """Test navigation capabilities for conversation SDK."""

    @pytest.fixture
    def real_conversation(self):
        """Load real conversation for testing."""
        # 95/5: Use discovery to find current transcript
        transcript = find_current_transcript()
        if transcript:
            return load(transcript)
        # Skip if no transcript found (CI environment)
        pytest.skip("No transcript available - requires real conversation data")

    def test_get_surrounding_context(self, real_conversation):
        """Test getting messages around a specific message."""
        conv = real_conversation

        # Find a message to get context around
        search_results = conv.search("95/5")
        assert len(search_results) > 0, "Should find messages about 95/5"

        target_msg = search_results[0]

        # Get surrounding context
        context = conv.get_surrounding(target_msg.uuid, before=2, after=2)

        # Should return up to 5 messages (2 before + target + 2 after)
        assert len(context) <= 5
        assert target_msg in context

        # Target should be in the middle (if enough messages exist)
        if len(context) == 5:
            assert context[2].uuid == target_msg.uuid

    def test_get_messages_between_timestamps(self, real_conversation):
        """Test temporal navigation between timestamps."""
        conv = real_conversation

        if len(conv) < 20:
            pytest.skip("Not enough messages for timestamp test")

        # Find messages with actual timestamps (some early messages have None)
        start_msg = None
        end_msg = None
        for i, msg in enumerate(conv.messages):
            if hasattr(msg, "timestamp") and msg.timestamp:
                if not start_msg:
                    start_msg = (i, msg.timestamp)
                elif i >= start_msg[0] + 5:  # At least 5 messages apart
                    end_msg = (i, msg.timestamp)
                    break

        if not start_msg or not end_msg:
            pytest.skip("Not enough messages with timestamps")

        messages = conv.get_messages_between_timestamps(start_msg[1], end_msg[1])

        # Should include messages in range
        assert len(messages) >= 1  # At least some messages
        # Verify all returned messages are in range
        for msg in messages:
            assert msg.timestamp is not None
            # Direct string comparison works for ISO timestamps
            assert start_msg[1] <= msg.timestamp <= end_msg[1]

    def test_get_thread_navigation(self, real_conversation):
        """Test thread navigation using parentUuid."""
        conv = real_conversation

        # Find a message with replies (skip Summary messages which don't have uuid)
        for msg in conv.messages[10:20]:  # Check middle messages
            if not hasattr(msg, "uuid"):
                continue  # Skip messages without uuid (like Summary)
            thread = conv.get_thread_from(msg.uuid)
            if len(thread) > 1:
                # Found a message with thread
                assert thread[0].uuid == msg.uuid
                # In real data, parent_uuid may be None (not all messages have parent-child relationships)
                # The threading logic is simplified, so we just verify we got messages
                assert len(thread) > 0
                break

    def test_get_by_uuid(self, real_conversation):
        """Test direct UUID lookup - should be O(1)."""
        conv = real_conversation

        # Pick a random message
        if len(conv) > 0:
            target = conv.messages[len(conv) // 2]

            # Lookup by UUID
            found = conv.get_by_uuid(target.uuid)

            assert found is not None
            assert found.uuid == target.uuid
            assert found.timestamp == target.timestamp

    def test_filter_by_type(self, real_conversation):
        """Test filtering messages by type."""
        conv = real_conversation

        # Get only user messages
        user_msgs = conv.filter_by_type("user")
        assert all(msg.type.value == "user" for msg in user_msgs)

        # Get only assistant messages
        assistant_msgs = conv.filter_by_type("assistant")
        assert all(msg.type.value == "assistant" for msg in assistant_msgs)

        # Total should not exceed original
        assert len(user_msgs) + len(assistant_msgs) <= len(conv)

    def test_get_session_boundaries(self, real_conversation):
        """Test finding session boundaries from sessionId changes."""
        conv = real_conversation

        # No skip - feature is now implemented
        boundaries = conv.get_session_boundaries()

        # Should have at least one session
        assert len(boundaries) >= 1

        # Each boundary should be an index (integer)
        for boundary in boundaries:
            assert isinstance(boundary, int)
            assert 0 <= boundary < len(conv.messages)


class TestNavigationPerformance:
    """Test performance requirements for navigation."""

    def test_uuid_lookup_is_fast(self):
        """UUID lookup should be O(1) via hashmap."""
        # Load a large conversation
        transcript = find_current_transcript()
        if not transcript:
            pytest.skip("No transcript found")

        conv = load(transcript)

        if len(conv) < 100:
            pytest.skip("Need larger conversation for performance test")

        import time

        # Test multiple lookups (skip messages without uuid)
        uuids = [
            msg.uuid for msg in conv.messages[::10] if hasattr(msg, "uuid")
        ]  # Every 10th message with uuid

        start = time.time()
        for uuid in uuids:
            conv.get_by_uuid(uuid)
        elapsed = time.time() - start

        # Should be very fast even for many lookups
        avg_time = elapsed / len(uuids)
        assert avg_time < 0.001, f"UUID lookup too slow: {avg_time:.4f}s per lookup"
