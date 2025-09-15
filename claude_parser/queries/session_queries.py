"""
Session queries - @SINGLE_SOURCE_TRUTH for JSONL loading operations.
Moved from storage/engine.py to follow SRP.
"""
from typing import Any, Dict, List
from ..storage.engine import get_engine


def load_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load JSONL file using DuckDB's native JSON reader.

    @FRAMEWORK_FIRST: 100% DuckDB delegation for JSON parsing.
    """
    engine = get_engine()
    result = engine.execute(
        "SELECT * FROM read_json_auto(?)",
        [jsonl_path]
    ).fetchall()

    # Convert to list of dicts for compatibility
    columns = [desc[0] for desc in engine.conn.description]
    messages = []
    for row in result:
        msg = dict(zip(columns, row))
        # Convert UUID objects to strings for Pydantic
        if 'uuid' in msg and msg['uuid']:
            msg['uuid'] = str(msg['uuid'])
        if 'parent_uuid' in msg and msg['parent_uuid']:
            msg['parent_uuid'] = str(msg['parent_uuid'])
        if 'parentUuid' in msg and msg['parentUuid']:
            msg['parentUuid'] = str(msg['parentUuid'])
        messages.append(msg)
    return messages