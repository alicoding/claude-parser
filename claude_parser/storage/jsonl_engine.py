#!/usr/bin/env python3
"""
JSONL Query Engine - 100% DuckDB delegation
@FRAMEWORK_FIRST: Use DuckDB's native read_json_auto
@SRP: ONLY executes SQL queries, no business logic
@LOC_ENFORCEMENT: <15 LOC
"""

import duckdb
from typing import Any


def query_jsonl(jsonl_path: str, where_clause: str = "") -> Any:
    """Query JSONL using DuckDB's native JSON support"""
    sql = f"SELECT * FROM read_json_auto('{jsonl_path}')"
    if where_clause:
        sql += f" WHERE {where_clause}"
    return duckdb.sql(sql).fetchall()