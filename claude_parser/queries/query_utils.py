#!/usr/bin/env python3
"""
Query utilities - @UTIL_FIRST reusable functions for all query modules.
@DRY_FIRST: Solves the schema mismatch problem ONCE.
@FRAMEWORK_FIRST: Uses Pydantic for schema normalization, not custom code.
"""
from typing import List, Any, Callable
from ..storage.engine import get_engine
from .schema_models import NormalizedMessage


def query_all_jsonl(jsonl_paths: List[str], query: str, params: List[Any] = None) -> List[Any]:
    """Query all JSONL files, handling schema differences.

    @UTIL_FIRST: This is THE utility for querying multiple JSONL files.
    Handles schema mismatches by querying each file separately.

    Args:
        jsonl_paths: List of JSONL file paths
        query: SQL query with ? placeholder for file path as FIRST param
        params: Additional parameters for the query

    Returns:
        Combined results from all files
    """
    engine = get_engine()
    all_results = []
    params = params or []

    for path in jsonl_paths:
        try:
            # File path is always first param, followed by user params
            full_params = [path] + params
            results = engine.execute(query, full_params).fetchall()
            all_results.extend(results)
        except Exception:
            # Skip files with incompatible schema
            continue

    return all_results


def query_with_sort(jsonl_paths: List[str], query: str, params: List[Any] = None,
                   sort_key: Callable = None, reverse: bool = True) -> List[Any]:
    """Query all JSONL files and sort results.

    @FRAMEWORK_FIRST: Delegates to query_all_jsonl then sorts.
    """
    results = query_all_jsonl(jsonl_paths, query, params)

    if sort_key:
        results.sort(key=sort_key, reverse=reverse)

    return results


def normalize_message(raw_data: dict) -> NormalizedMessage:
    """@FRAMEWORK_FIRST: Use Pydantic to normalize JSONL message schemas."""
    return NormalizedMessage.parse_obj(raw_data)