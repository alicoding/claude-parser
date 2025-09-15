"""
Query modules - @SINGLE_SOURCE_TRUTH: One file per feature.
Each module contains SQL queries for its specific domain.
All modules delegate to storage.engine.execute() for DuckDB access.
"""