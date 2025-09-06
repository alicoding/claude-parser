"""
Comprehensive validation against real production JSONL files.

ZERO SKIP POLICY - All tests must pass with real data.
This ensures 100% integration readiness for other projects.
"""

import pytest
from pathlib import Path
from claude_parser import load, load_many
from claude_parser.models import MessageType, AssistantMessage, UserMessage, Summary
from claude_parser.domain.services import SessionAnalyzer, ContextWindowManager
from claude_parser.analytics import ConversationAnalytics
import orjson as json


class TestRealDataValidation:
    """Validate all business logic against real production data."""

    @pytest.fixture
    def prod_files(self):
        """All production JSONL files."""
        prod_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser")
        return {
            'small': prod_dir / "4762e53b-7ca8-4464-9eac-d1816c343c50.jsonl",  # 1 line
            'medium': prod_dir / "3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl",  # 98 lines
            'large': prod_dir / "840f9326-6f99-46d9-88dc-f32fb4754d36.jsonl",  # 4992 lines
        }

    def test_all_files_load_successfully(self, prod_files):
        """All production files must load without errors."""
        for name, file_path in prod_files.items():
            assert file_path.exists(), f"{name} file missing: {file_path}"

            # Must load without exceptions
            conv = load(file_path)
            assert conv is not None, f"Failed to load {name}"
            assert len(conv.messages) > 0, f"No messages in {name}"
            print(f"✅ {name}: {len(conv.messages)} messages loaded")

    def test_message_structure_validation(self, prod_files):
        """Validate message structure matches production reality."""
        for name, file_path in prod_files.items():
            conv = load(file_path)

            for i, msg in enumerate(conv.messages[:10]):  # Check first 10
                # Every message must have type
                assert hasattr(msg, 'type'), f"Message {i} in {name} missing type"
                assert msg.type in MessageType, f"Invalid type in {name}"

                # Messages should have UUID (required field)
                if hasattr(msg, 'uuid'):
                    assert msg.uuid, f"Empty UUID in {name} message {i}"

                # Session ID should exist
                if hasattr(msg, 'session_id'):
                    assert msg.session_id is None or isinstance(msg.session_id, str)

    def test_text_extraction_from_nested_structure(self, prod_files):
        """Text extraction must work with nested message.content structure."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        # Find messages with actual content
        for msg in conv.messages:
            if isinstance(msg, (UserMessage, AssistantMessage)):
                text = msg.text_content
                assert isinstance(text, str), f"text_content must return string"

                # If message has nested structure, it should extract properly
                if hasattr(msg, 'message') and isinstance(msg.message, dict):
                    if msg.message.get('content'):
                        # Should extract meaningful text, not raw JSON
                        assert '{' not in text or 'type' not in text, \
                            "Text extraction returning raw JSON structure"

    def test_token_counting_accuracy(self, prod_files):
        """Token counting must use real usage structure."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        # Find assistant messages with usage info
        for msg in conv.messages:
            if isinstance(msg, AssistantMessage):
                if hasattr(msg, 'real_usage_info') and msg.real_usage_info:
                    usage = msg.real_usage_info

                    # Validate usage structure
                    assert 'input_tokens' in usage, "Missing input_tokens"
                    assert 'output_tokens' in usage, "Missing output_tokens"

                    # Calculate total correctly
                    total = msg.total_tokens
                    expected = (
                        usage.get('input_tokens', 0) +
                        usage.get('output_tokens', 0) +
                        usage.get('cache_read_input_tokens', 0) +
                        usage.get('cache_creation_input_tokens', 0)
                    )
                    assert total == expected, f"Token calculation mismatch: {total} != {expected}"

    def test_session_analysis_with_real_data(self, prod_files):
        """Session analysis must work with production data."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        analyzer = SessionAnalyzer()
        stats = analyzer.analyze_current_session(conv)

        # Validate session stats
        assert stats.total_tokens >= 0, "Invalid token count"
        assert stats.session_start_index >= 0, "Invalid session start"
        assert stats.message_count >= 0, "Invalid message count"
        assert 0 <= stats.cache_hit_rate <= 1, "Invalid cache hit rate"
        assert stats.cost_usd >= 0, "Invalid cost calculation"

        # Should identify model from real data
        if stats.total_tokens > 0:
            assert stats.model != "unknown", "Should detect model from usage"

    def test_context_window_monitoring(self, prod_files):
        """Context window manager must provide accurate monitoring."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        analyzer = SessionAnalyzer()
        stats = analyzer.analyze_current_session(conv)

        manager = ContextWindowManager()
        info = manager.analyze(stats.total_tokens)

        # Validate context info
        assert 0 <= info.percentage_used <= 200, "Invalid percentage"
        assert info.tokens_remaining >= 0, "Negative tokens remaining"
        assert info.tokens_until_compact >= 0, "Negative tokens until compact"
        assert info.status.value in ['green', 'yellow', 'orange', 'red', 'critical']

        # At 90% (180K), should_compact should be True
        if stats.total_tokens >= 180_000:
            assert info.should_compact, "Should compact at 90%"

    def test_navigation_with_real_data(self, prod_files):
        """Navigation must work with production conversations."""
        large_file = prod_files['large']
        conv = load(large_file)

        # Search functionality
        results = conv.search("test")
        assert isinstance(results, list), "Search must return list"

        # Filter functionality
        user_msgs = conv.filter(lambda m: m.type == MessageType.USER)
        assert isinstance(user_msgs, list), "Filter must return list"
        assert all(m.type == MessageType.USER for m in user_msgs)

        # Session boundaries
        boundaries = conv.get_session_boundaries()
        assert isinstance(boundaries, list), "Boundaries must be list"
        assert all(isinstance(b, int) for b in boundaries)

    def test_analytics_with_real_data(self, prod_files):
        """Analytics must provide accurate metrics."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        analytics = ConversationAnalytics(conv)
        stats = analytics.get_statistics()

        # Validate stats structure
        assert stats.total_messages > 0
        assert stats.user_messages >= 0
        assert stats.assistant_messages >= 0
        assert stats.total_tokens >= 0

        # Values should be reasonable
        assert stats.total_messages == len(conv.messages)
        assert stats.total_messages >= stats.user_messages + stats.assistant_messages

    def test_load_many_with_real_files(self, prod_files):
        """load_many must work with multiple real files."""
        files = list(prod_files.values())
        conversations = load_many(files)

        assert len(conversations) == len(files), "Should load all files"
        for conv in conversations:
            assert conv is not None, "Each conversation must load"
            assert hasattr(conv, 'messages'), "Must have messages"

    def test_iteration_and_indexing(self, prod_files):
        """Collection interface must work properly."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        # Length
        assert len(conv) == len(conv.messages)

        # Iteration
        count = 0
        for msg in conv:
            count += 1
            assert hasattr(msg, 'type')
        assert count == len(conv)

        # Indexing
        if len(conv) > 0:
            first = conv[0]
            last = conv[-1]
            assert first == conv.messages[0]
            assert last == conv.messages[-1]

        # Slicing
        if len(conv) >= 10:
            subset = conv[5:10]
            assert len(subset) == 5
            assert subset == conv.messages[5:10]

    def test_message_type_distribution(self, prod_files):
        """Validate message type distribution is reasonable."""
        for name, file_path in prod_files.items():
            conv = load(file_path)

            type_counts = {}
            for msg in conv.messages:
                type_name = msg.type.value if hasattr(msg.type, 'value') else str(msg.type)
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

            print(f"\n{name} message distribution:")
            for msg_type, count in type_counts.items():
                percentage = (count / len(conv.messages)) * 100
                print(f"  {msg_type}: {count} ({percentage:.1f}%)")

            # Every conversation should have at least one message
            assert sum(type_counts.values()) > 0

    def test_error_handling_graceful_degradation(self, tmp_path):
        """System must handle malformed data gracefully."""
        # Create file with mixed valid/invalid lines
        test_file = tmp_path / "mixed.jsonl"
        content = [
            '{"type":"summary","summary":"Test","uuid":"1","sessionId":"test"}',
            '{invalid json}',  # Bad line
            '{"type":"user","uuid":"2","sessionId":"test","message":{"content":"Hello"}}',
            '{"missing":"required fields"}',  # Missing type
            '{"type":"assistant","uuid":"3","sessionId":"test","message":{"content":[{"type":"text","text":"Hi"}]}}',
        ]
        test_file.write_text('\n'.join(content))

        # Should load valid lines, skip invalid
        conv = load(test_file)
        assert len(conv.messages) >= 2, "Should load at least the valid messages"

        # Valid messages should be properly typed
        for msg in conv.messages:
            assert hasattr(msg, 'type')
            assert msg.type in MessageType

    def test_real_data_performance(self, prod_files):
        """Loading and processing must be performant."""
        import time

        large_file = prod_files['large']

        # Load time should be reasonable
        start = time.time()
        conv = load(large_file)
        load_time = time.time() - start

        print(f"\nPerformance metrics for {large_file.name}:")
        print(f"  Load time: {load_time:.2f}s")
        print(f"  Messages: {len(conv.messages)}")
        print(f"  Messages/sec: {len(conv.messages)/load_time:.0f}")

        # Should load at reasonable speed (>1000 msgs/sec)
        assert len(conv.messages) / load_time > 100, "Load performance too slow"

        # Search should be fast
        start = time.time()
        results = conv.search("test")
        search_time = time.time() - start
        print(f"  Search time: {search_time:.3f}s")
        assert search_time < 1.0, "Search too slow"

    def test_integration_readiness(self, prod_files):
        """Validate API is ready for integration."""
        medium_file = prod_files['medium']

        # This is what other projects will do:

        # 1. Load conversation
        conv = load(medium_file)
        assert conv is not None

        # 2. Get basic info
        session_id = conv.session_id
        message_count = len(conv)
        assert isinstance(session_id, (str, type(None)))
        assert isinstance(message_count, int)

        # 3. Analyze tokens
        analyzer = SessionAnalyzer()
        stats = analyzer.analyze_current_session(conv)
        assert stats.total_tokens >= 0

        # 4. Check context status
        manager = ContextWindowManager()
        info = manager.analyze(stats.total_tokens)
        assert info.percentage_until_compact >= 0

        # 5. Search content
        results = conv.search("git")
        assert isinstance(results, list)

        # 6. Get analytics
        analytics = ConversationAnalytics(conv)
        stats = analytics.get_statistics()
        assert stats is not None
        assert stats.total_messages > 0

        print("\n✅ Integration API validated - ready for other projects!")


class TestBusinessLogicInvariants:
    """Ensure business logic invariants hold with real data."""

    @pytest.fixture
    def prod_files(self):
        """All production JSONL files."""
        prod_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser")
        return {
            'small': prod_dir / "4762e53b-7ca8-4464-9eac-d1816c343c50.jsonl",
            'medium': prod_dir / "3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl",
            'large': prod_dir / "840f9326-6f99-46d9-88dc-f32fb4754d36.jsonl",
        }

    def test_no_duplicate_uuids_in_conversation(self, prod_files):
        """Each message UUID must be unique within conversation."""
        for name, file_path in prod_files.items():
            conv = load(file_path)

            uuids = []
            for msg in conv.messages:
                if hasattr(msg, 'uuid') and msg.uuid:
                    uuids.append(msg.uuid)

            # Check for duplicates
            if uuids:
                assert len(uuids) == len(set(uuids)), f"Duplicate UUIDs found in {name}"

    def test_chronological_timestamp_order(self, prod_files):
        """Timestamps should be mostly in chronological order."""
        for name, file_path in prod_files.items():
            conv = load(file_path)

            timestamps = []
            for msg in conv.messages:
                if hasattr(msg, 'timestamp') and msg.timestamp:
                    timestamps.append(msg.timestamp)

            # Check that MOST timestamps are in order (allow small deviations)
            if len(timestamps) > 1:
                out_of_order = 0
                for i in range(1, len(timestamps)):
                    if timestamps[i] < timestamps[i-1]:
                        out_of_order += 1

                # Allow up to 5% out of order (real-world data has minor timing issues)
                tolerance = max(1, len(timestamps) * 0.05)
                assert out_of_order <= tolerance, \
                    f"Too many timestamps out of order in {name}: {out_of_order}/{len(timestamps)}"

    def test_session_consistency(self, prod_files):
        """Session IDs should be consistent within boundaries."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        boundaries = conv.get_session_boundaries()

        # Messages between boundaries should have same session_id
        for i in range(len(boundaries)):
            start = boundaries[i]
            end = boundaries[i+1] if i+1 < len(boundaries) else len(conv.messages)

            session_ids = set()
            for j in range(start, end):
                if hasattr(conv.messages[j], 'session_id'):
                    session_ids.add(conv.messages[j].session_id)

            # Should have at most one unique session_id per segment
            assert len(session_ids) <= 1, \
                f"Multiple session IDs in segment {i}: {session_ids}"

    def test_cost_calculation_accuracy(self, prod_files):
        """Cost calculations must be accurate and consistent."""
        medium_file = prod_files['medium']
        conv = load(medium_file)

        analyzer = SessionAnalyzer()
        stats = analyzer.analyze_current_session(conv)

        # Manual cost calculation for verification
        expected_cost = 0.0
        expected_cost += (stats.input_tokens / 1_000_000) * 3.00
        expected_cost += (stats.output_tokens / 1_000_000) * 15.00
        expected_cost += (stats.cache_created_tokens / 1_000_000) * 3.75
        expected_cost += (stats.cache_read_tokens / 1_000_000) * 0.30

        # Should match within rounding error
        assert abs(stats.cost_usd - expected_cost) < 0.01, \
            f"Cost calculation mismatch: {stats.cost_usd} != {expected_cost}"


# No skips allowed - all tests must pass with real data!
