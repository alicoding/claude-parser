"""TodoParser - Single Responsibility: Parse JSON.

95% library (orjson), 5% glue.
"""
import orjson
from typing import List, Dict, Union


class TodoParser:
    """Parse todos from various formats. No I/O, pure functions."""
    
    @staticmethod
    def parse(data: Union[str, bytes]) -> List[Dict]:
        """Parse TodoWrite output into list of todo dicts.
        
        Args:
            data: JSON string or bytes from TodoWrite tool
            
        Returns:
            List of todo dictionaries
            
        Raises:
            orjson.JSONDecodeError: If data is not valid JSON
        """
        # orjson handles bytes natively (95% library)
        if isinstance(data, str):
            data = data.encode()
        
        parsed = orjson.loads(data)
        
        # Handle both formats: array or {todos: [...]}
        if isinstance(parsed, list):
            return parsed
        return parsed.get("todos", [])