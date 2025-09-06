"""
Semantic search for Claude Parser codebase.

95/5: Using llama-index for semantic search
SOLID: Single responsibility - only semantic search
"""

from .search import SemanticSearch

__all__ = ["SemanticSearch"]
