"""
DuckDB Storage Engine - @SINGLE_SOURCE_TRUTH for DuckDB connection ONLY.

This is the ONLY file that imports DuckDB. Provides execute() for raw SQL.
ANTI-PATTERN WARNING: Do NOT add business logic here! Each feature should
have its own query module in queries/ that uses engine.execute().
"""
import duckdb
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageEngine:
    """@SINGLE_SOURCE_TRUTH: Only this class knows about DuckDB."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize DuckDB connection."""
        self.db_path = db_path or ":memory:"
        self.conn = duckdb.connect(str(self.db_path))
    
    def execute(self, sql: str, params: Optional[List[Any]] = None) -> Any:
        """Execute raw SQL query - delegates to DuckDB.

        Args:
            sql: SQL query string
            params: Optional parameters for prepared statement

        Returns:
            Query result from DuckDB

        Example:
            result = engine.execute("SELECT * FROM read_json_auto(?)", [jsonl_path])
        """
        if params:
            return self.conn.execute(sql, params)
        return self.conn.execute(sql)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Singleton instance
_engine: Optional[StorageEngine] = None

def get_engine(db_path: Optional[Path] = None) -> StorageEngine:
    """Get or create storage engine instance."""
    global _engine
    if _engine is None:
        _engine = StorageEngine(db_path)
    return _engine