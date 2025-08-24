"""Tests for discovery domain."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from claude_parser.discovery import (
    find_current_transcript,
    find_transcript_for_cwd,
    list_all_projects,
    find_project_by_original_path,
    find_project_by_encoded_name,
)


class TestDiscoveryFunctions:
    """Test discovery domain functions."""
    
    @patch('claude_parser.discovery.transcript_finder.Path.cwd')
    @patch('claude_parser.discovery.transcript_finder.find_transcript_for_cwd')
    def test_find_current_transcript(self, mock_find, mock_cwd):
        """Test finding transcript for current directory."""
        mock_cwd.return_value = Path("/test/project")
        mock_find.return_value = "/path/to/transcript.jsonl"
        
        result = find_current_transcript()
        
        assert result == "/path/to/transcript.jsonl"
        mock_find.assert_called_once_with(Path("/test/project"))
    
    @patch('claude_parser.discovery.transcript_finder.Path.home')
    def test_find_transcript_for_cwd_not_found(self, mock_home):
        """Test when Claude projects directory doesn't exist."""
        mock_home.return_value = Path("/fake/home")
        
        result = find_transcript_for_cwd(Path("/test/project"))
        
        assert result is None
    
    @patch('claude_parser.discovery.transcript_finder.Path.home')
    def test_list_all_projects_empty(self, mock_home):
        """Test listing projects when none exist."""
        mock_home.return_value = Path("/fake/home")
        
        projects = list_all_projects()
        
        assert projects == []
    
    @patch('claude_parser.discovery.transcript_finder.list_all_projects')
    def test_find_project_by_original_path(self, mock_list):
        """Test finding project by original path."""
        mock_list.return_value = [
            {
                "original_path": "/test/project",
                "encoded_name": "-test-project",
                "transcripts": []
            },
            {
                "original_path": "/other/project",
                "encoded_name": "-other-project",
                "transcripts": []
            }
        ]
        
        result = find_project_by_original_path("/test/project")
        
        assert result is not None
        assert result["original_path"] == "/test/project"
        assert result["encoded_name"] == "-test-project"
    
    @patch('claude_parser.discovery.transcript_finder.list_all_projects')
    def test_find_project_by_encoded_name(self, mock_list):
        """Test finding project by encoded name."""
        mock_list.return_value = [
            {
                "original_path": "/test/project",
                "encoded_name": "-test-project",
                "transcripts": []
            },
            {
                "original_path": "/other/project",
                "encoded_name": "-other-project",
                "transcripts": []
            }
        ]
        
        result = find_project_by_encoded_name("-other-project")
        
        assert result is not None
        assert result["original_path"] == "/other/project"
        assert result["encoded_name"] == "-other-project"
    
    @patch('claude_parser.discovery.transcript_finder.list_all_projects')
    def test_find_project_by_original_path_not_found(self, mock_list):
        """Test finding project that doesn't exist."""
        mock_list.return_value = []
        
        result = find_project_by_original_path("/nonexistent")
        
        assert result is None
    
    @patch('claude_parser.discovery.transcript_finder.list_all_projects')
    def test_find_project_by_encoded_name_not_found(self, mock_list):
        """Test finding project by encoded name that doesn't exist."""
        mock_list.return_value = []
        
        result = find_project_by_encoded_name("-nonexistent")
        
        assert result is None


class TestDiscoveryWithRealData:
    """Test discovery with real Claude Code data if available."""
    
    def test_list_all_projects_real(self):
        """Test listing real projects if they exist."""
        projects = list_all_projects()
        
        # This will vary by environment
        if projects:
            # If projects exist, verify structure
            for project in projects:
                assert "original_path" in project
                assert "encoded_name" in project
                assert "transcripts" in project
                assert isinstance(project["transcripts"], list)
    
    def test_find_current_transcript_real(self):
        """Test finding current transcript in real environment."""
        # This test will pass regardless of whether transcript exists
        transcript = find_current_transcript()
        
        if transcript:
            assert isinstance(transcript, str)
            assert transcript.endswith(".jsonl")