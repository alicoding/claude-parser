"""
TodoDomain for parsing and manipulating Claude's TodoWrite format.

Handles multi-project todo management with session and agent tracking.
File naming convention: {session-id}-agent-{agent-id}.json
"""

from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import orjson
from pydantic import BaseModel, Field
from toolz import filter as toolz_filter, map as toolz_map
from more_itertools import first as more_first
import pendulum

from claude_parser.discovery.transcript_finder import find_current_transcript, find_project_by_original_path


class TodoStatus(Enum):
    """Todo status states matching Claude's TodoWrite tool."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(Enum):
    """Todo priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Todo(BaseModel):
    """Single todo item matching Claude's format."""
    content: str
    status: TodoStatus = TodoStatus.PENDING
    activeForm: str
    priority: TodoPriority = TodoPriority.MEDIUM
    id: str = ""

    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.COMPLETED

    @property
    def is_in_progress(self) -> bool:
        return self.status == TodoStatus.IN_PROGRESS

    @property
    def is_pending(self) -> bool:
        return self.status == TodoStatus.PENDING


class TodoSession(BaseModel):
    """Represents a todo file with session/agent information."""
    session_id: str
    agent_id: str
    file_path: Path
    project_path: Optional[Path] = None
    todos: List[Todo] = Field(default_factory=list)

    @classmethod
    def from_file_path(cls, file_path: Path) -> "TodoSession":
        """Parse session and agent IDs from filename."""
        # Pattern: {session-id}-agent-{agent-id}.json
        name = file_path.stem
        parts = name.split("-agent-")

        if len(parts) == 2:
            session_id = parts[0]
            agent_id = parts[1]
        else:
            # Fallback for non-standard names
            session_id = name
            agent_id = name

        return cls(
            session_id=session_id,
            agent_id=agent_id,
            file_path=file_path
        )

    def get_filename(self) -> str:
        """Generate standard filename for this session."""
        return f"{self.session_id}-agent-{self.agent_id}.json"


class TodoDomain:
    """Parse and manipulate Claude's TodoWrite format with multi-project support."""

    @staticmethod
    def parse(todo_json: str | bytes) -> List[Todo]:
        """Parse TodoWrite tool output into Todo objects.

        Args:
            todo_json: JSON string or bytes from TodoWrite tool

        Returns:
            List of Todo objects
        """
        if isinstance(todo_json, str):
            todo_json = todo_json.encode()

        data = orjson.loads(todo_json)

        # Handle both formats: direct array or {todos: [...]}
        if isinstance(data, list):
            todos_data = data
        else:
            todos_data = data.get("todos", [])

        return [Todo(**todo) for todo in todos_data]

    @staticmethod
    def format_for_claude(todos: List[Dict] | List[Todo]) -> str:
        """Format todos for ~/.claude/todos/*.json.

        Args:
            todos: List of todo dicts or Todo objects

        Returns:
            JSON string formatted for Claude
        """
        # Convert Todo objects to dicts if needed
        if todos and isinstance(todos[0], Todo):
            todos = [t.model_dump(mode='json') for t in todos]

        # Ensure status is string not enum
        for todo in todos:
            if "status" in todo and hasattr(todo["status"], "value"):
                todo["status"] = todo["status"].value
            if "priority" in todo and hasattr(todo["priority"], "value"):
                todo["priority"] = todo["priority"].value

        return orjson.dumps(todos, option=orjson.OPT_INDENT_2).decode()

    @staticmethod
    def get_session_from_cwd() -> Tuple[Optional[str], Optional[str]]:
        """Get session and project info from current working directory.

        Uses transcript_finder to map cwd to session.

        Returns:
            Tuple of (session_id, project_path) or (None, None) if not found
        """
        transcript = find_current_transcript()
        if not transcript:
            return None, None

        # Extract session ID from transcript path
        transcript_path = Path(transcript)
        session_id = transcript_path.stem

        # Get project path from transcript finder
        project_info = find_project_by_original_path(Path.cwd())
        project_path = project_info["original_path"] if project_info else str(Path.cwd())

        return session_id, project_path

    @staticmethod
    def load_todos_for_session(session_id: str) -> List[TodoSession]:
        """Load all todo files for a given session.

        Args:
            session_id: Session UUID

        Returns:
            List of TodoSession objects with todos loaded
        """
        todos_dir = Path.home() / ".claude" / "todos"
        if not todos_dir.exists():
            return []

        # Find all files for this session
        pattern = f"{session_id}-agent-*.json"
        session_files = list(todos_dir.glob(pattern))

        # Also check for exact match (same session and agent ID)
        exact_file = todos_dir / f"{session_id}-agent-{session_id}.json"
        if exact_file.exists() and exact_file not in session_files:
            session_files.append(exact_file)

        sessions = []
        for file_path in session_files:
            session = TodoSession.from_file_path(file_path)

            # Load todos from file
            try:
                content = file_path.read_bytes()
                session.todos = TodoDomain.parse(content)
            except Exception:
                # Keep empty todos list if parse fails
                pass

            sessions.append(session)

        return sessions

    @staticmethod
    def generate_todos(
        task_description: str,
        context: Dict,
        options: Dict = None
    ) -> List[Dict]:
        """Generate todos from task description and context.

        Args:
            task_description: Natural language task description
            context: Context dict with flags like requires_research, tdd_required
            options: Additional options for todo generation

        Returns:
            List of todo dicts ready for TodoWrite tool
        """
        todos = []
        options = options or {}

        # Add research todo if needed
        if context.get("requires_research"):
            todos.append({
                "content": f"Research solutions for {task_description}",
                "status": "pending",
                "activeForm": f"Researching solutions for {task_description}",
                "priority": "high",
                "id": f"research-{_generate_id()}"
            })

        # Add test todo if TDD
        if context.get("tdd_required"):
            todos.append({
                "content": "Write tests first",
                "status": "pending",
                "activeForm": "Writing tests first",
                "priority": "high",
                "id": f"test-{_generate_id()}"
            })

        # Main implementation
        todos.append({
            "content": f"Implement {task_description}",
            "status": "pending",
            "activeForm": f"Implementing {task_description}",
            "priority": "medium",
            "id": f"impl-{_generate_id()}"
        })

        # Add validation
        if not options.get("skip_validation"):
            todos.append({
                "content": "Validate implementation",
                "status": "pending",
                "activeForm": "Validating implementation",
                "priority": "low",
                "id": f"validate-{_generate_id()}"
            })

        return todos

    @staticmethod
    def calculate_progress(todos: List[Todo] | List[Dict]) -> Dict:
        """Calculate progress metrics from todos.

        Args:
            todos: List of Todo objects or dicts

        Returns:
            Progress metrics dict
        """
        # Convert dicts to Todo objects if needed
        if todos and isinstance(todos[0], dict):
            todos = [Todo(**t) for t in todos]

        total = len(todos)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "percentage": 0,
                "current": None
            }

        completed = sum(1 for t in todos if t.is_completed)
        in_progress = sum(1 for t in todos if t.is_in_progress)
        pending = total - completed - in_progress

        # Find current task
        current_task = more_first(
            toolz_filter(lambda t: t.is_in_progress, todos),
            default=None
        )

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": round((completed / total * 100), 1),
            "current": current_task.content if current_task else None,
            "current_id": current_task.id if current_task else None
        }

    @staticmethod
    def diff(old_todos: List[Dict], new_todos: List[Dict]) -> List[Dict]:
        """Find changes between todo states.

        Args:
            old_todos: Previous todo state
            new_todos: New todo state

        Returns:
            List of changes with action descriptions
        """
        changes = []

        # Create maps by ID or content
        def get_key(todo):
            return todo.get("id") or todo.get("content")

        old_map = {get_key(t): t for t in old_todos}
        new_map = {get_key(t): t for t in new_todos}

        # Find changes
        for key, new_todo in new_map.items():
            old_todo = old_map.get(key)

            if not old_todo:
                # New todo added
                changes.append({
                    "action": "added",
                    "todo": new_todo["content"],
                    "status": new_todo["status"]
                })
            elif old_todo["status"] != new_todo["status"]:
                # Status changed
                changes.append({
                    "action": "status_changed",
                    "todo": new_todo["content"],
                    "old_status": old_todo["status"],
                    "new_status": new_todo["status"],
                    "transition": f"{old_todo['status']} -> {new_todo['status']}"
                })

        # Find removed todos
        for key, old_todo in old_map.items():
            if key not in new_map:
                changes.append({
                    "action": "removed",
                    "todo": old_todo["content"],
                    "status": old_todo["status"]
                })

        return changes

    @staticmethod
    def inject_todos(todos: List[Dict], session_id: str = None, agent_id: str = None):
        """Write todos directly to Claude's directory.

        Args:
            todos: List of todo dicts
            session_id: Session UUID (auto-detected if not provided)
            agent_id: Agent UUID (uses session_id if not provided)
        """
        # Auto-detect session if not provided
        if not session_id:
            session_id, _ = TodoDomain.get_session_from_cwd()
            if not session_id:
                raise ValueError("Cannot detect session ID. Provide explicitly or run from project with transcript.")

        # Default agent_id to session_id
        if not agent_id:
            agent_id = session_id

        # Create todos directory
        todos_dir = Path.home() / ".claude" / "todos"
        todos_dir.mkdir(parents=True, exist_ok=True)

        # Format and write
        formatted = TodoDomain.format_for_claude(todos)
        todo_file = todos_dir / f"{session_id}-agent-{agent_id}.json"
        todo_file.write_text(formatted)

        return str(todo_file)


def _generate_id() -> str:
    """Generate a short ID for todos."""
    return pendulum.now().format("HHmmss")
