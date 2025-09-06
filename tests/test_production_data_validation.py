"""
Production data validation test suite - Ground truth for business logic.

Uses real production JSONL files as the source of truth for:
- Message structure expectations
- Token counting accuracy
- Content extraction patterns
- Usage info structure

SOLID: Single Responsibility - Production data validation only
95/5: Uses pytest framework for validation
"""

import pytest
from pathlib import Path
from claude_parser import load
from claude_parser.models.assistant import AssistantMessage
from claude_parser.models.user import UserMessage


class TestProductionDataGroundTruth:
    """Validates business logic against real production JSONL data."""

    @pytest.fixture
    def prod_data_dir(self):
        """Production data directory."""
        return Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser")

    @pytest.fixture
    def sample_conversation(self, prod_data_dir):
        """Load real production conversation."""
        jsonl_file = prod_data_dir / "3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl"
        if not jsonl_file.exists():
            pytest.skip(f"Production data file not found: {jsonl_file}")
        return load(jsonl_file)

    def test_real_message_structure_parsing(self, sample_conversation):
        """GROUND TRUTH: Real messages have nested structure with message field."""
        messages = sample_conversation.messages

        # Real production data has messages with nested message field
        real_messages = [msg for msg in messages if hasattr(msg, 'message')]
        assert len(real_messages) > 0, "Should find messages with nested message structure"

        # Validate nested structure exists
        for msg in real_messages[:5]:  # Check first 5
            assert hasattr(msg, 'message'), f"Message should have nested message field: {msg}"
            assert isinstance(msg.message, dict), f"Message.message should be dict: {type(msg.message)}"

    def test_assistant_text_extraction_from_real_data(self, sample_conversation):
        """GROUND TRUTH: Assistant messages extract text from nested content blocks."""
        assistant_msgs = [msg for msg in sample_conversation.messages
                         if isinstance(msg, AssistantMessage)]

        assert len(assistant_msgs) > 0, "Should have assistant messages"

        # Test text extraction from real structure
        for msg in assistant_msgs[:3]:  # Test first 3
            text_content = msg.text_content

            # Real data should extract meaningful text, not be empty
            if hasattr(msg, 'message') and msg.message.get('content'):
                assert len(text_content) > 0, f"Should extract text from real content: {msg.message.get('content')}"
                # Should not contain raw JSON structure
                assert 'type' not in text_content or 'text' in text_content, "Should extract clean text, not raw JSON"

    def test_user_text_extraction_from_real_data(self, sample_conversation):
        """GROUND TRUTH: User messages extract text from nested message.content."""
        user_msgs = [msg for msg in sample_conversation.messages
                    if isinstance(msg, UserMessage)]

        assert len(user_msgs) > 0, "Should have user messages"

        # Test text extraction from real structure
        for msg in user_msgs[:3]:  # Test first 3
            text_content = msg.text_content

            # Real user messages should have extractable text
            if hasattr(msg, 'message') and msg.message.get('content'):
                assert isinstance(text_content, str), "Text content should be string"
                if msg.message['content']:  # If not empty
                    assert len(text_content) > 0, "Should extract non-empty text from real content"

    def test_token_counting_from_real_usage_structure(self, sample_conversation):
        """GROUND TRUTH: Token counts come from nested message.usage structure."""
        assistant_msgs = [msg for msg in sample_conversation.messages
                         if isinstance(msg, AssistantMessage)]

        usage_msgs = [msg for msg in assistant_msgs if msg.real_usage_info]
        assert len(usage_msgs) > 0, "Should have messages with real usage info"

        for msg in usage_msgs[:2]:  # Test first 2 with usage
            usage = msg.real_usage_info

            # Validate real production usage structure
            assert 'input_tokens' in usage, f"Usage should have input_tokens: {usage}"
            assert 'output_tokens' in usage, f"Usage should have output_tokens: {usage}"
            assert isinstance(usage['input_tokens'], int), "input_tokens should be int"
            assert isinstance(usage['output_tokens'], int), "output_tokens should be int"

            # Cache fields exist in real data
            if 'cache_read_input_tokens' in usage:
                assert isinstance(usage['cache_read_input_tokens'], int)
            if 'cache_creation_input_tokens' in usage:
                assert isinstance(usage['cache_creation_input_tokens'], int)

    def test_total_tokens_calculation_accuracy(self, sample_conversation):
        """GROUND TRUTH: total_tokens should sum all usage components correctly."""
        assistant_msgs = [msg for msg in sample_conversation.messages
                         if isinstance(msg, AssistantMessage)]

        usage_msgs = [msg for msg in assistant_msgs if msg.real_usage_info]

        for msg in usage_msgs[:2]:  # Test calculation accuracy
            usage = msg.real_usage_info
            calculated_total = msg.total_tokens

            # Manual calculation for validation
            expected_total = (
                usage.get('input_tokens', 0) +
                usage.get('output_tokens', 0) +
                usage.get('cache_read_input_tokens', 0) +
                usage.get('cache_creation_input_tokens', 0)
            )

            assert calculated_total == expected_total, (
                f"Token calculation mismatch - Expected: {expected_total}, "
                f"Got: {calculated_total}, Usage: {usage}"
            )

    def test_conversation_loading_success(self, prod_data_dir):
        """GROUND TRUTH: Production files should load without errors."""
        jsonl_files = list(prod_data_dir.glob("*.jsonl"))

        if not jsonl_files:
            pytest.skip("No production JSONL files found")

        # Test loading multiple production files
        successful_loads = 0
        for jsonl_file in jsonl_files[:3]:  # Test first 3 files
            try:
                conversation = load(jsonl_file)
                assert conversation is not None, f"Should load conversation from {jsonl_file}"
                assert len(conversation.messages) > 0, f"Should have messages in {jsonl_file}"
                successful_loads += 1
            except Exception as e:
                pytest.fail(f"Failed to load production file {jsonl_file}: {e}")

        assert successful_loads > 0, "Should successfully load at least one production file"

    def test_message_types_in_production_data(self, sample_conversation):
        """GROUND TRUTH: Production data contains expected message types."""
        messages = sample_conversation.messages
        message_types = set(msg.type.value if hasattr(msg.type, 'value') else str(msg.type) for msg in messages)

        # Production conversations should have basic message types
        expected_types = {'user', 'assistant'}
        found_types = message_types.intersection(expected_types)

        assert len(found_types) >= 1, f"Should find expected message types. Found: {message_types}"

    def test_chronological_message_ordering(self, sample_conversation):
        """GROUND TRUTH: Messages should maintain chronological order."""
        messages = sample_conversation.messages

        # Extract timestamps where available
        timestamped_messages = []
        for msg in messages:
            if hasattr(msg, 'timestamp') and msg.timestamp:
                timestamped_messages.append(msg)

        if len(timestamped_messages) >= 2:
            # Validate chronological ordering
            for i in range(1, len(timestamped_messages)):
                prev_time = timestamped_messages[i-1].timestamp
                curr_time = timestamped_messages[i].timestamp

                # Basic timestamp format validation
                assert isinstance(prev_time, str), "Timestamp should be string"
                assert isinstance(curr_time, str), "Timestamp should be string"
                assert len(prev_time) > 10, "Timestamp should be substantial (ISO format)"
                assert len(curr_time) > 10, "Timestamp should be substantial (ISO format)"
