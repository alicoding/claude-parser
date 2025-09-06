"""
Tests for LlamaIndex export functionality.

Tests the service request requirements for project-wide memory export.
"""

import tempfile
from pathlib import Path

import orjson
import pytest

from claude_parser import ProjectConversationExporter
from claude_parser.export.llamaindex_exporter import Document, PatternDetector


class TestProjectConversationExporter:
    """Test the main export functionality."""

    @pytest.fixture
    def sample_conversation_jsonl(self):
        """Create a sample JSONL file with various message types."""
        messages = [
            # User question
            {
                "type": "user",
                "uuid": "user-1",
                "timestamp": "2024-01-01T10:00:00Z",
                "sessionId": "test-session",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "What's the best architecture for our API?"}]
                }
            },
            # Assistant response with decision
            {
                "type": "assistant",
                "uuid": "asst-1",
                "timestamp": "2024-01-01T10:00:10Z",
                "sessionId": "test-session",
                "model": "claude-3",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "We should use FastAPI for the backend. It provides async support and automatic documentation."}]
                }
            },
            # Tool use (should be filtered)
            {
                "type": "user",
                "uuid": "user-2",
                "timestamp": "2024-01-01T10:01:00Z",
                "sessionId": "test-session",
                "message": {
                    "role": "user",
                    "content": [{"type": "tool_result", "content": "File: api.py created successfully"}]
                }
            },
            # Learning moment
            {
                "type": "assistant",
                "uuid": "asst-2",
                "timestamp": "2024-01-01T10:02:00Z",
                "sessionId": "test-session",
                "model": "claude-3",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "I discovered that using dependency injection makes the code much more testable."}]
                }
            },
        ]

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.jsonl', delete=False) as f:
            for msg in messages:
                f.write(orjson.dumps(msg))
                f.write(b'\n')
            return Path(f.name)

    def test_export_basic(self, sample_conversation_jsonl):
        """Test basic export functionality."""
        # Create exporter with the directory containing the JSONL
        project_path = sample_conversation_jsonl.parent
        exporter = ProjectConversationExporter(project_path)

        # Export documents
        documents = exporter.export()

        # Should have documents (Q&A pair + insight)
        assert len(documents) > 0

        # Check document structure
        for doc in documents:
            assert isinstance(doc, Document)
            assert hasattr(doc, 'text')
            assert hasattr(doc, 'metadata')
            assert 'timestamp' in doc.metadata
            assert 'conversation_id' in doc.metadata
            assert 'type' in doc.metadata

    def test_tool_filtering(self, sample_conversation_jsonl):
        """Test that tool messages are filtered out."""
        project_path = sample_conversation_jsonl.parent
        exporter = ProjectConversationExporter(
            project_path,
            config={"exclude_tool_use": True}
        )

        documents = exporter.export()

        # Check that no documents contain tool-related content
        for doc in documents:
            assert "File: api.py created" not in doc.text
            assert "tool_result" not in doc.text.lower()

    def test_pattern_detection(self):
        """Test pattern detection for decisions, mistakes, learnings."""
        test_cases = [
            ("We decided to use React", "decision"),
            ("I learned that caching improves performance", "learning"),
            ("That was wrong, we should have used TypeScript", "mistake"),
            ("Let's pivot to a microservices architecture", "pivot"),
            ("How do I install Python?", "qa"),  # Default
        ]

        for text, expected_type in test_cases:
            detected_type = PatternDetector.classify_message(text)
            assert detected_type == expected_type

    def test_document_metadata(self, sample_conversation_jsonl):
        """Test that documents have proper metadata."""
        project_path = sample_conversation_jsonl.parent
        exporter = ProjectConversationExporter(project_path)

        documents = exporter.export()

        # Check first document metadata
        if documents:
            doc = documents[0]
            assert 'timestamp' in doc.metadata
            assert 'conversation_id' in doc.metadata
            assert 'type' in doc.metadata
            assert 'project' in doc.metadata

            # Type should be one of the expected values
            assert doc.metadata['type'] in [
                'decision', 'learning', 'mistake', 'pivot', 'qa',
                'insight_decision', 'insight_learning', 'insight_mistake', 'insight_pivot'
            ]

    def test_llamaindex_compatibility(self, sample_conversation_jsonl):
        """Test that documents are compatible with LlamaIndex."""
        project_path = sample_conversation_jsonl.parent
        exporter = ProjectConversationExporter(project_path)

        documents = exporter.export()

        # Documents should be convertible to dict
        for doc in documents:
            doc_dict = doc.to_dict()
            assert 'text' in doc_dict
            assert 'metadata' in doc_dict
            assert isinstance(doc_dict['metadata'], dict)

    def test_empty_project(self):
        """Test handling of project with no JSONL files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ProjectConversationExporter(tmpdir)
            documents = exporter.export()
            assert documents == []

    def test_config_options(self, sample_conversation_jsonl):
        """Test various configuration options."""
        project_path = sample_conversation_jsonl.parent

        # Test with insights disabled
        exporter = ProjectConversationExporter(
            project_path,
            config={"include_insights": False}
        )

        documents = exporter.export()

        # Should still have Q&A pairs
        assert any('Q:' in doc.text for doc in documents)


class TestPatternDetector:
    """Test the pattern detection functionality."""

    def test_decision_patterns(self):
        """Test detection of decision patterns."""
        decisions = [
            "We decided to implement caching",
            "I'll use PostgreSQL for the database",
            "The best approach is to use Docker",
            "Let's go with the microservices architecture",
        ]

        for text in decisions:
            assert PatternDetector.classify_message(text) == "decision"

    def test_learning_patterns(self):
        """Test detection of learning patterns."""
        learnings = [
            "I learned that async isn't always faster",
            "Discovered a new way to optimize queries",
            "Now I understand why DDD is important",
            "Interesting that Python has pattern matching",
        ]

        for text in learnings:
            assert PatternDetector.classify_message(text) == "learning"

    def test_mistake_patterns(self):
        """Test detection of mistake patterns."""
        mistakes = [
            "That was wrong, I should have checked first",
            "The bug was in the authentication logic",
            "The issue is with the database connection",
            "My mistake was not writing tests first",
        ]

        for text in mistakes:
            assert PatternDetector.classify_message(text) == "mistake"

    def test_pivot_patterns(self):
        """Test detection of pivot patterns."""
        pivots = [
            "Actually, let's switch to GraphQL",
            "On second thought, we should use Redis",
            "We pivoted from monolith to microservices",
            "Instead of REST, let's use gRPC",
        ]

        for text in pivots:
            assert PatternDetector.classify_message(text) == "pivot"

    def test_default_qa(self):
        """Test that unmatched patterns default to Q&A."""
        generic = [
            "How do I install Python?",
            "What is the capital of France?",
            "Can you explain decorators?",
        ]

        for text in generic:
            assert PatternDetector.classify_message(text) == "qa"
