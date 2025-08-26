"""Tests for unused modules to improve coverage.

These modules are not currently used but exist in the codebase.
Testing them ensures they work if needed in the future.
"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from claude_parser.application.conversation_service import (
    ConversationFilterOptions,
    ConversationSearchOptions,
    ConversationService,
)
from claude_parser.infrastructure.message_repository import JsonlMessageRepository


class TestInfrastructureMessageRepository:
    """Test the infrastructure message repository."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=b'{"type": "user", "uuid": "test-123", "session_id": "session-123", "message": {"role": "user", "content": "test"}}\n',
    )
    @patch("claude_parser.infrastructure.message_repository.orjson.loads")
    def test_load_messages(self, mock_loads, mock_file):
        """Test loading messages from JSONL."""
        mock_loads.return_value = {
            "type": "user",
            "uuid": "test-123",
            "session_id": "session-123",
            "message": {"role": "user", "content": "test"},
        }

        repo = JsonlMessageRepository()
        messages = repo.load_messages(Path("test.jsonl"))

        assert len(messages) == 1
        mock_file.assert_called_once_with(Path("test.jsonl"), "rb")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_messages_file_not_found(self, mock_file):
        """Test handling of missing file."""
        repo = JsonlMessageRepository()

        with pytest.raises(FileNotFoundError):
            repo.load_messages(Path("nonexistent.jsonl"))

    @patch("builtins.open", new_callable=mock_open, read_data=b"invalid json\n")
    def test_load_messages_invalid_json(self, mock_file):
        """Test handling of invalid JSON."""
        repo = JsonlMessageRepository()
        messages = repo.load_messages(Path("test.jsonl"))

        # Should skip invalid lines
        assert len(messages) == 0

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=b'{"type": "user", "uuid": "test-123", "session_id": "test-123", "cwd": "/test/dir", "gitBranch": "main", "message": {"role": "user", "content": "test"}}\n',
    )
    def test_get_metadata(self, mock_file):
        """Test metadata extraction."""
        repo = JsonlMessageRepository()

        # Load messages to populate raw messages for metadata extraction
        messages = repo.load_messages(Path("test.jsonl"))

        # Get metadata from the loaded messages
        metadata = repo.get_metadata(messages, Path("test.jsonl"))

        assert metadata.session_id == "test-123"
        assert metadata.current_dir == "/test/dir"
        assert metadata.git_branch == "main"
        assert metadata.filepath == Path("test.jsonl")


class TestApplicationConversationService:
    """Test the application conversation service."""

    def test_service_initialization(self):
        """Test service initialization."""
        mock_repo = MagicMock()
        service = ConversationService(mock_repo)

        assert service.repository == mock_repo

    def test_load_conversation(self):
        """Test loading a conversation."""
        mock_repo = MagicMock()
        mock_repo.load_messages.return_value = [
            MagicMock(type="user"),
            MagicMock(type="assistant"),
        ]
        mock_repo.get_metadata.return_value = {
            "session_id": "test-123",
            "current_dir": "/test",
            "git_branch": "main",
            "filepath": Path("test.jsonl"),
        }

        service = ConversationService(mock_repo)
        conv = service.load_conversation(Path("test.jsonl"))

        assert conv is not None
        mock_repo.load_messages.assert_called_once_with(Path("test.jsonl"))

    def test_search_conversations(self):
        """Test searching conversations."""
        mock_repo = MagicMock()
        service = ConversationService(mock_repo)

        mock_conv = MagicMock()
        mock_conv.search.return_value = [MagicMock(), MagicMock()]

        options = ConversationSearchOptions(query="test", case_sensitive=False)

        results = service.search_conversation(mock_conv, options)

        assert results is not None
        mock_conv.search.assert_called_once()

    def test_filter_conversations(self):
        """Test filtering conversations."""
        mock_repo = MagicMock()
        service = ConversationService(mock_repo)

        # Mock conversations list
        mock_conversations = [MagicMock(), MagicMock()]
        for conv in mock_conversations:
            conv.search.return_value = ["message1", "message2"]

        filter_options = ConversationFilterOptions(contains_text="test")

        results = service.filter_conversations(mock_conversations, filter_options)

        assert results is not None
        assert len(results) == 2  # Both conversations match

    def test_analyze_conversation(self):
        """Test analyzing a conversation."""
        mock_repo = MagicMock()
        service = ConversationService(mock_repo)

        mock_conv = MagicMock()
        mock_conv.__len__ = MagicMock(return_value=100)
        mock_conv.assistant_messages = [MagicMock()] * 50
        mock_conv.user_messages = [MagicMock()] * 45
        mock_conv.tool_uses = [MagicMock()] * 5
        mock_conv.with_errors = MagicMock(return_value=[])
        mock_conv.session_id = "test-123"
        mock_conv.summaries = []

        analysis = service.analyze_conversation(mock_conv)

        assert analysis["total_messages"] == 100
        assert analysis["assistant_messages"] == 50
        assert analysis["user_messages"] == 45
