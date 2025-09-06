"""
TEMPORARY semantic search implementation.

This is a minimal implementation until semantic-search-service SDK is ready.
See docs/SEMANTIC_SEARCH_INTEGRATION.md for migration plan.

LIMITATIONS:
- Only indexes 10 files to avoid rate limits
- 7 RPM rate limit for ElectronHub free tier
- 3-minute cooldown on rate limit violations
- No caching or persistence
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import httpx
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from loguru import logger
import numpy as np


class ElectronHubEmbedding(BaseEmbedding):
    """Custom embedding for ElectronHub API with rate limiting."""

    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small", rpm: int = 7):
        """Initialize with ElectronHub settings and rate limiting."""
        super().__init__(
            model_name=model_name,
            embed_batch_size=1  # Process one at a time for rate limiting
        )
        self._api_key = api_key
        self._base_url = "https://api.electronhub.ai/v1"
        self._client = httpx.Client(timeout=30.0)
        self._rpm = rpm  # Requests per minute
        self._last_request_time = 0
        self._request_count = 0
        self._minute_start = time.time()
        self._cooldown_until = 0

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()

        # Check if in cooldown
        if now < self._cooldown_until:
            wait_time = self._cooldown_until - now
            logger.warning(f"In cooldown, waiting {wait_time:.0f}s")
            time.sleep(wait_time)
            now = time.time()
            self._minute_start = now
            self._request_count = 0

        # Reset counter if new minute
        if now - self._minute_start >= 60:
            self._minute_start = now
            self._request_count = 0

        # Wait if at rate limit
        if self._request_count >= self._rpm:
            wait_time = 60 - (now - self._minute_start)
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.0f}s")
                time.sleep(wait_time)
                self._minute_start = time.time()
                self._request_count = 0

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for single text with rate limiting."""
        self._wait_for_rate_limit()

        try:
            response = self._client.post(
                f"{self._base_url}/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"input": text, "model": self.model_name}
            )
            response.raise_for_status()
            self._request_count += 1
            return response.json()["data"][0]["embedding"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Set 3-minute cooldown
                self._cooldown_until = time.time() + 180
                logger.error(f"Rate limit hit, 3-minute cooldown started")
            else:
                logger.error(f"HTTP error: {e}")
            return [0.0] * 1536
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [0.0] * 1536

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self._get_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self._get_embedding(text)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async query embedding."""
        return self._get_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async text embedding."""
        return self._get_embedding(text)


class SemanticSearch:
    """Semantic search for Claude Parser codebase."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize with lightweight indexing."""
        self.project_path = Path(project_path or Path.cwd())

        # Configure embeddings with ElectronHub
        api_key = os.getenv("ELECTRONHUB_API_KEY")

        if not api_key:
            logger.warning("No ELECTRONHUB_API_KEY found")
            self.index = None
            return

        Settings.chunk_size = 512  # Smaller chunks for accuracy
        Settings.chunk_overlap = 50
        Settings.embed_model = ElectronHubEmbedding(api_key)

        self.index = None
        self._index_codebase()

    def _index_codebase(self, max_files: int = 10):
        """Index Claude Parser codebase with rate limit awareness."""
        logger.info(f"Indexing {self.project_path} (max {max_files} files)")

        documents = []
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "build", "dist", "tests"}
        file_count = 0

        # Index core Python files first
        core_paths = [
            "claude_parser/domain/todo",
            "claude_parser/hooks",
            "claude_parser/models"
        ]

        for core_path in core_paths:
            path = self.project_path / core_path
            if not path.exists():
                continue

            for py_file in path.rglob("*.py"):
                if file_count >= max_files:
                    break

                if any(skip in py_file.parts for skip in skip_dirs):
                    continue

                try:
                    content = py_file.read_text()
                    rel_path = py_file.relative_to(self.project_path)

                    doc = Document(
                        text=content[:2000],  # Limit content size
                        metadata={
                            "file_path": str(rel_path),
                            "file_type": "python",
                            "module": str(rel_path).replace("/", ".").replace(".py", "")
                        }
                    )
                    documents.append(doc)
                    file_count += 1
                    logger.debug(f"Indexed: {rel_path}")
                except Exception as e:
                    logger.debug(f"Skip {py_file}: {e}")

        # Index key markdown docs if space
        if file_count < max_files:
            for md_file in ["README.md", "CLAUDE.md", "SPECIFICATION.md"]:
                if file_count >= max_files:
                    break

                md_path = self.project_path / md_file
                if md_path.exists():
                    try:
                        content = md_path.read_text()
                        doc = Document(
                            text=content[:2000],
                            metadata={"file_path": md_file, "file_type": "markdown"}
                        )
                        documents.append(doc)
                        file_count += 1
                        logger.debug(f"Indexed: {md_file}")
                    except Exception as e:
                        logger.debug(f"Skip {md_file}: {e}")

        if documents:
            logger.info(f"Creating index from {len(documents)} documents...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                transformations=[SentenceSplitter(chunk_size=256, chunk_overlap=20)]
            )
            logger.info(f"Successfully indexed {len(documents)} files")
        else:
            logger.warning("No documents to index")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search codebase with semantic query."""
        if not self.index:
            return []

        query_engine = self.index.as_query_engine(
            response_mode="retrieval",
            similarity_top_k=top_k
        )

        response = query_engine.query(query)

        results = []
        for node in response.source_nodes:
            results.append({
                "file": node.metadata.get("file_path", "unknown"),
                "score": node.score,
                "content": node.text[:300],
                "metadata": node.metadata
            })

        return results
