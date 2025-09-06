"""
Tests for semantic search functionality.

TDD: Testing semantic search capabilities
95/5: Using pytest for testing
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from claude_parser.semantic import SemanticSearch


class TestSemanticSearch:
    """Test semantic search functionality."""

    @patch("claude_parser.semantic.search.VectorStoreIndex")
    @patch("claude_parser.semantic.search.Document")
    def test_init_indexes_codebase(self, mock_doc, mock_index):
        """Test that initialization indexes the codebase."""
        searcher = SemanticSearch()

        assert searcher.project_path == Path.cwd()
        assert mock_doc.called
        assert mock_index.from_documents.called

    @patch("claude_parser.semantic.search.VectorStoreIndex")
    def test_search_returns_results(self, mock_index):
        """Test search returns formatted results."""
        # Setup mock
        mock_node = MagicMock()
        mock_node.metadata = {"file_path": "test.py"}
        mock_node.score = 0.95
        mock_node.text = "test content"

        mock_response = MagicMock()
        mock_response.source_nodes = [mock_node]

        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = mock_response

        mock_index_instance = MagicMock()
        mock_index_instance.as_query_engine.return_value = mock_query_engine
        mock_index.from_documents.return_value = mock_index_instance

        searcher = SemanticSearch()
        searcher.index = mock_index_instance

        results = searcher.search("test query")

        assert len(results) == 1
        assert results[0]["file"] == "test.py"
        assert results[0]["score"] == 0.95
        assert "test content" in results[0]["content"]

    @patch("claude_parser.semantic.search.VectorStoreIndex")
    def test_search_with_no_index(self, mock_index):
        """Test search with no index returns empty."""
        searcher = SemanticSearch()
        searcher.index = None

        results = searcher.search("test query")

        assert results == []

    @patch("claude_parser.semantic.search.VectorStoreIndex")
    def test_search_top_k_limit(self, mock_index):
        """Test search respects top_k parameter."""
        # Setup multiple mock nodes
        mock_nodes = []
        for i in range(10):
            node = MagicMock()
            node.metadata = {"file_path": f"test{i}.py"}
            node.score = 0.9 - i * 0.1
            node.text = f"content {i}"
            mock_nodes.append(node)

        mock_response = MagicMock()
        mock_response.source_nodes = mock_nodes[:3]  # Return only 3

        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = mock_response

        mock_index_instance = MagicMock()
        mock_index_instance.as_query_engine.return_value = mock_query_engine
        mock_index.from_documents.return_value = mock_index_instance

        searcher = SemanticSearch()
        searcher.index = mock_index_instance

        results = searcher.search("test query", top_k=3)

        assert len(results) == 3
        mock_index_instance.as_query_engine.assert_called_with(
            response_mode="retrieval",
            similarity_top_k=3
        )
