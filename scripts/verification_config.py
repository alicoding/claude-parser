"""
Configuration for 95/5 Principle Verification
SOLID: Single Responsibility - Just configuration, no logic
"""

# ANSI color codes
COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "RESET": "\033[0m"
}

# Approved libraries - Update this list to add/remove approved libraries
APPROVED_LIBRARIES = {
    # Core (required)
    "orjson", "pydantic", "pendulum", "loguru", "httpx", "watchfiles",
    
    # Data processing (approved)
    "toolz", "more-itertools", "more_itertools", "networkx", 
    "lazy_object_proxy", "lazy-object-proxy",
    
    # CLI/Config (approved)
    "typer", "rich", "pydantic-settings", "pydantic_settings",
    
    # Testing (approved)
    "pytest", "pytest-cov", "pytest_cov",
    
    # Development (approved)
    "ruff", "mypy", "mkdocs", "mkdocs-material", "mkdocs_material", 
    "pre-commit", "pre_commit",
    
    # Utilities (approved)
    "tenacity", "python-dotenv", "dotenv",
    
    # Additional approved libraries
    "dependency_injector", "jmespath", "jsonlines", "deepdiff", "git",
    "mem0", "m0", "GitPython", "gitpython",
    
    # Python stdlib modules (allowed)
    "sys", "os", "pathlib", "typing", "re", "subprocess", "hashlib",
    "dataclasses", "abc", "collections", "enum", "functools", "itertools",
    "operator",  # For methodcaller, attrgetter, etc.
    "ast",  # For AST parsing
    "json",  # Only for type hints, not actual use
    "tempfile",  # High-level temp file management
    "io",  # For StringIO and file-like objects
    "mmap",  # Memory-mapped file handling (stdlib)
    "random",  # Random sampling (stdlib)
    "time",  # Time operations (stdlib)
    
    # Token counting (approved)
    "tiktoken",  # OpenAI's token counter for LLMs
    
    # Internal modules (allowed)
    "verification_config",  # Our own config file
}

# Forbidden import patterns
FORBIDDEN_IMPORTS = [
    # JSON - must use orjson
    (r"^import json(?:\s|$)", "Use orjson instead of json"),
    (r"^from json import", "Use orjson instead of json"),
    
    # HTTP - must use httpx
    (r"^import requests(?:\s|$)", "Use httpx instead of requests"),
    (r"^import urllib", "Use httpx instead of urllib"),
    (r"^from urllib", "Use httpx instead of urllib"),
    
    # Dates - must use pendulum
    (r"^from datetime import", "Use pendulum instead of datetime"),
    (r"^import datetime(?:\s|$)", "Use pendulum instead of datetime"),
    
    # ASYNC/THREADING - COMPLETELY FORBIDDEN
    (r"^import asyncio", "NO ASYNC - we're a sync library"),
    (r"^from asyncio", "NO ASYNC - we're a sync library"),
    (r"^import threading", "NO THREADING - use high-level libraries"),
    (r"^from threading import", "NO THREADING - use high-level libraries"),
    (r"^import multiprocessing", "NO MULTIPROCESSING - stay simple"),
    (r"^from multiprocessing", "NO MULTIPROCESSING - stay simple"),
    (r"^import concurrent", "NO CONCURRENT - we're synchronous"),
    (r"^from concurrent", "NO CONCURRENT - we're synchronous"),
    (r"async def", "NO ASYNC FUNCTIONS - we're synchronous"),
    (r"await ", "NO AWAIT - we're synchronous"),
    
    # Logging - must use loguru
    (r"^import logging(?:\s|$)", "Use loguru instead of logging"),
    (r"^from logging import", "Use loguru instead of logging"),
    
    # Config - must use pydantic
    (r"^import argparse", "Use typer or click instead of argparse"),
    (r"^import configparser", "Use pydantic-settings instead"),
    
    # Progress - must use rich
    (r"^import tqdm", "Use rich.progress instead of tqdm"),
    (r"^from tqdm", "Use rich.progress instead of tqdm"),
    
    # Low-level operations
    (r"^import struct", "Too low-level - find a high-level library"),
    (r"^import ctypes", "Too low-level - find a high-level library"),
    (r"^import socket", "Use httpx instead of raw sockets"),
]

# Forbidden code patterns (95/5 violations)
FORBIDDEN_PATTERNS = [
    (r"\[.*for .* in .*\]", 
     "BLOCKED: List comprehension detected!\n    ACTION REQUIRED: Use toolz.map and toolz.filter"),
    
    (r"for .* in .*:", 
     "BLOCKED: Manual for-loop detected!\n    ACTION REQUIRED: Use toolz.map or toolz.pipe"),
    
    (r"\.append\(", 
     "BLOCKED: Manual list building detected!\n    ACTION REQUIRED: Use toolz.concat or functional building"),
    
    (r"\.extend\(", 
     "BLOCKED: Manual extend detected!\n    ACTION REQUIRED: Use toolz.concat or more-itertools.flatten"),
    
    (r"while .*:", 
     "BLOCKED: While loop detected!\n    ACTION REQUIRED: Use toolz.iterate or recursive approach"),
    
    (r"break(?:\s|$)", 
     "BLOCKED: Break statement!\n    ACTION REQUIRED: Use toolz.take_while"),
    
    (r"continue(?:\s|$)", 
     "BLOCKED: Continue statement!\n    ACTION REQUIRED: Use toolz.filter to skip items"),
    
    (r"= \[\]", 
     "BLOCKED: Empty list initialization!\n    ACTION REQUIRED: Use functional operations without mutable state"),
    
    (r"= \{\}", 
     "BLOCKED: Empty dict/set initialization!\n    ACTION REQUIRED: Use toolz.merge or functional operations"),
    
    (r"\+= 1", 
     "BLOCKED: Manual increment!\n    ACTION REQUIRED: Use toolz.count or functional counting"),
    
    (r"\.clear\(\)", 
     "BLOCKED: Mutation via clear()!\n    ACTION REQUIRED: Create new immutable data instead"),
     
    (r"\.extend\(", 
     "BLOCKED: Manual extend!\n    ACTION REQUIRED: Use toolz.concat or functional building"),
]



# Required test files
REQUIRED_TESTS = [
    "test_parser.py",
    "test_models.py", 
    "test_api.py",
]

# Paths to check
PATHS = {
    "source": "claude_parser",
    "scripts": "scripts",
    "tests": "tests",
    "typescript": "packages/core/src",
}

# Files to exclude from checks
EXCLUDED_FILES = [
    "__pycache__",
    ".pyc",
    ".pyo",
    "test_",  # Test files have different rules
    "verification_config.py",  # Config file contains pattern definitions
    "async_watcher.py",  # Async is intentional for watch feature
    "sse_helpers.py",  # SSE needs async
    "timeline.py",  # Legacy code, will refactor later
    "memory/",  # Memory export feature, will refactor later
]

# Exemptions for specific files
EXEMPTIONS = {
    # Add file-specific exemptions here if needed
    # "specific_file.py": ["pattern_to_exempt"]
}
