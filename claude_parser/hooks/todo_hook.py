"""
TodoHook helper for PostToolUse:TodoWrite integration.

Provides utilities for parsing hook data and formatting responses.
"""

import sys
from typing import Dict, Optional, Any
import orjson
import pendulum
from pathlib import Path

from claude_parser.domain.todo import TodoDomain, Todo


class TodoHookHelper:
    """Helper for PostToolUse:TodoWrite hook integration."""

    @staticmethod
    def parse_hook_data(stdin_data: str | bytes) -> Dict:
        """Parse data from PostToolUse hook.

        Handles various formats Claude might send:
        - Direct todo array
        - Object with todos field
        - Tool response format

        Args:
            stdin_data: Raw input from hook stdin

        Returns:
            Parsed data dict with todos field
        """
        if isinstance(stdin_data, str):
            stdin_data = stdin_data.encode()

        try:
            data = orjson.loads(stdin_data)

            # Handle different formats
            if isinstance(data, list):
                # Direct array of todos
                return {"todos": data}
            elif isinstance(data, dict):
                if "todos" in data:
                    # Already has todos field
                    return data
                elif "tool" in data and "inputs" in data:
                    # Tool response format
                    return data["inputs"]
                elif "content" in data or "status" in data:
                    # Single todo item
                    return {"todos": [data]}
                else:
                    # Unknown format, return as-is
                    return data
            else:
                return {"todos": [], "error": f"Unexpected data type: {type(data)}"}

        except orjson.JSONDecodeError as e:
            return {"todos": [], "error": f"Parse failed: {e}"}
        except Exception as e:
            return {"todos": [], "error": f"Unexpected error: {e}"}

    @staticmethod
    def format_response(
        success: bool,
        message: str = "",
        data: Optional[Dict] = None
    ) -> str:
        """Format response for hook.

        Args:
            success: Whether operation succeeded
            message: Human-readable message
            data: Additional data to include

        Returns:
            JSON string response
        """
        response = {
            "success": success,
            "message": message,
            "timestamp": pendulum.now().isoformat()
        }

        if data:
            response.update(data)

        return orjson.dumps(response).decode()

    @staticmethod
    def sync_to_dstask(todos: list, project_path: str = None) -> Dict[str, Any]:
        """Sync todos to dstask.

        Args:
            todos: List of Todo objects or dicts
            project_path: Project path for tagging

        Returns:
            Sync results dict
        """
        import subprocess

        # Calculate progress
        progress = TodoDomain.calculate_progress(todos)

        # Determine project tag
        if project_path:
            project_path = Path(project_path)
            if "claude-parser" in str(project_path):
                project_tag = "+claude-parser"
            elif "temporal-hooks" in str(project_path):
                project_tag = "+temporal-hooks"
            elif "task-enforcer" in str(project_path):
                project_tag = "+task-enforcer"
            else:
                project_tag = "+shared"
        else:
            project_tag = "+shared"

        results = {
            "synced": [],
            "errors": [],
            "progress": progress
        }

        # Get existing dstask items
        try:
            result = subprocess.run(
                ["dstask", "show-open", project_tag],
                capture_output=True,
                text=True,
                timeout=5
            )
            existing_tasks = result.stdout
        except Exception as e:
            results["errors"].append(f"Failed to get dstask items: {e}")
            return results

        # Sync current in-progress task
        if progress["current"]:
            # Try to find and update matching task
            for line in existing_tasks.split('\n'):
                if progress["current"] in line:
                    # Extract task ID (first field)
                    parts = line.strip().split()
                    if parts and parts[0].isdigit():
                        task_id = parts[0]

                        # Update task note with progress
                        note = f"Progress: {progress['completed']}/{progress['total']} ({progress['percentage']}%)"
                        try:
                            subprocess.run(
                                ["dstask", task_id, "note", note],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            results["synced"].append({
                                "task_id": task_id,
                                "content": progress["current"],
                                "note": note
                            })
                        except Exception as e:
                            results["errors"].append(f"Failed to update task {task_id}: {e}")
                    break

        return results

    @staticmethod
    def handle_hook() -> int:
        """Main entry point for PostToolUse:TodoWrite hook.

        Reads from stdin, processes todos, and writes response to stdout.

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            # Read input
            stdin_data = sys.stdin.read()

            # Parse todos
            data = TodoHookHelper.parse_hook_data(stdin_data)

            if "error" in data:
                print(TodoHookHelper.format_response(False, data["error"]))
                return 1

            # Parse todos using TodoDomain
            todos = TodoDomain.parse(orjson.dumps(data))

            # Calculate progress
            progress = TodoDomain.calculate_progress(todos)

            # Try to sync to dstask (optional)
            sync_results = None
            try:
                # Get project path from session
                session_id, project_path = TodoDomain.get_session_from_cwd()
                if session_id:
                    sync_results = TodoHookHelper.sync_to_dstask(todos, project_path)
            except Exception:
                # Sync is optional, don't fail hook
                pass

            # Format response
            response_data = {
                "progress": progress,
                "todo_count": len(todos)
            }

            if sync_results:
                response_data["sync"] = sync_results

            message = f"Processed {len(todos)} todos. "
            if progress["current"]:
                message += f"Current: {progress['current']} "
            message += f"({progress['completed']}/{progress['total']} completed)"

            print(TodoHookHelper.format_response(True, message, response_data))
            return 0

        except Exception as e:
            print(TodoHookHelper.format_response(False, f"Hook failed: {e}"))
            return 1
