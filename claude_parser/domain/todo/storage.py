"""TodoStorage - Single Responsibility: File I/O.

95% library (pathlib, orjson), 5% glue.
"""

from pathlib import Path
from typing import Dict, List, Optional

import orjson


class TodoStorage:
    """Handle todo file storage. No business logic, just I/O."""

    def __init__(self, session_id: str, agent_id: Optional[str] = None):
        """Initialize with session and agent IDs.

        Args:
            session_id: Session UUID from transcript
            agent_id: Agent UUID (defaults to session_id)
        """
        self.session_id = session_id
        self.agent_id = agent_id or session_id
        self.todos_dir = Path.home() / ".claude" / "todos"

    def get_path(self) -> Path:
        """Get todo file path."""
        filename = f"{self.session_id}-agent-{self.agent_id}.json"
        return self.todos_dir / filename

    def read(self) -> List[Dict]:
        """Read todos from file.

        Returns:
            List of todo dicts, empty list if file doesn't exist
        """
        path = self.get_path()
        if not path.exists():
            return []

        # orjson does the work (95% library)
        return orjson.loads(path.read_bytes())

    def write(self, todos: List[Dict]) -> str:
        """Write todos to file.

        Args:
            todos: List of todo dictionaries

        Returns:
            Path to written file
        """
        self.todos_dir.mkdir(parents=True, exist_ok=True)
        path = self.get_path()

        # orjson handles formatting (95% library)
        formatted = orjson.dumps(todos, option=orjson.OPT_INDENT_2)
        path.write_bytes(formatted)

        return str(path)

    def delete(self) -> bool:
        """Delete todo file.

        Returns:
            True if deleted, False if didn't exist
        """
        path = self.get_path()
        if path.exists():
            path.unlink()
            return True
        return False
