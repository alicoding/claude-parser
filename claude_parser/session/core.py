#!/usr/bin/env python3
"""
Session Manager - DuckDB Delegation via Storage Engine
@SINGLE_SOURCE_TRUTH: Only storage/engine.py reads JSONL
@COMPOSITION: Returns plain dicts, no shared types
"""

from pathlib import Path
from typing import List, Dict, Any


class SessionManager:
    """Delegates to DuckDB storage engine - @SINGLE_SOURCE_TRUTH"""
    
    def __init__(self):
        """Initialize with storage engine delegation"""
        from ..storage.engine import get_engine
        self.engine = get_engine()
    
    def load_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """Delegate to DuckDB engine for JSONL loading"""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return []

        # @SINGLE_SOURCE_TRUTH: Delegate to queries module
        from ..queries.session_queries import load_jsonl
        return load_jsonl(file_path)
    
    def extract_message_types(self, raw_data: List[Dict[str, Any]]) -> List[str]:
        """Extract message types from plain dicts"""
        if not raw_data:
            return []
        
        # @COMPOSITION: Process plain dicts, no framework needed
        types = []
        for msg in raw_data:
            msg_type = msg.get('type') or msg.get('role') or 'unknown'
            types.append(msg_type)
        return types
    
    def extract_session_metadata(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from plain dicts"""
        if not raw_data:
            return {"total_events": 0, "types": [], "has_uuid": False}
        
        types = self.extract_message_types(raw_data)
        has_uuid = any('uuid' in msg or 'id' in msg for msg in raw_data)
        
        return {
            "total_events": len(raw_data),
            "types": list(set(types)),
            "has_uuid": has_uuid
        }
    
    def _create_rich_message(self, msg_dict: Dict[str, Any]):
        """@COMPOSITION: Return plain dict"""
        return msg_dict
    
