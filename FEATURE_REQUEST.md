# Feature Request: Todo Domain for TodoWrite Integration

## 🎯 Overview
Create a new domain in claude-parser to parse and manipulate Claude's TodoWrite tool format, enabling bidirectional sync between Claude's todos and external task management systems.

## 📋 Requirements

### 1. Parse TodoWrite Format
```python
# Input: Claude's TodoWrite tool output
{
    "todos": [
        {
            "content": "Research rate limiting libraries",
            "status": "pending",
            "activeForm": "Researching rate limiting libraries"
        },
        {
            "content": "Implement rate limiter",
            "status": "in_progress",
            "activeForm": "Implementing rate limiter"
        }
    ]
}

# Parse into structured domain objects
todos = TodoDomain.parse(todo_json)
assert todos[0].content == "Research rate limiting libraries"
assert todos[1].is_in_progress == True
```

### 2. Generate Todos from Task Context
```python
# Generate todos from task description and context
task = Task(
    description="Add rate limiting to API",
    requires_research=True,
    requires_testing=True,
    complexity="medium"
)

todos = TodoDomain.generate_todos(task)
# Returns properly formatted todos for TodoWrite tool
```

### 3. Track Todo State Changes
```python
# Detect what changed between todo updates
old_todos = [{"content": "Research", "status": "pending"}, ...]
new_todos = [{"content": "Research", "status": "completed"}, ...]

changes = TodoDomain.diff(old_todos, new_todos)
assert changes[0].action == "completed"
assert changes[0].todo == "Research"
```

### 4. Map Todos to External Tasks
```python
# Maintain mapping between todos and task IDs
mapper = TodoTaskMapper()
mapper.link_todo("Research libraries", task_id=89)

# Later, when todo updates come from hook
task_id = mapper.get_task_id("Research libraries")
assert task_id == 89
```

## 🏗 Proposed Implementation

### Domain Structure
```python
# claude_parser/domains/todo.py
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Todo(BaseModel):
    content: str
    status: TodoStatus
    activeForm: str
    
    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.COMPLETED
    
    @property
    def is_in_progress(self) -> bool:
        return self.status == TodoStatus.IN_PROGRESS

class TodoDomain:
    """Parse and manipulate Claude's TodoWrite format"""
    
    @staticmethod
    def parse(todo_json: str) -> List[Todo]:
        """Parse TodoWrite tool output into Todo objects"""
        data = orjson.loads(todo_json)
        todos = data.get("todos", [])
        return [Todo(**todo) for todo in todos]
    
    @staticmethod
    def generate_todos(
        task_description: str,
        context: Dict,
        options: Dict = None
    ) -> List[Dict]:
        """Generate todos from task description and context"""
        todos = []
        
        # Add research todo if needed
        if context.get("requires_research"):
            todos.append({
                "content": f"Research solutions for {task_description}",
                "status": "pending",
                "activeForm": f"Researching solutions for {task_description}"
            })
        
        # Add test todo if TDD
        if context.get("tdd_required"):
            todos.append({
                "content": "Write tests first",
                "status": "pending",
                "activeForm": "Writing tests first"
            })
        
        # Main implementation
        todos.append({
            "content": f"Implement {task_description}",
            "status": "pending",
            "activeForm": f"Implementing {task_description}"
        })
        
        # Validation
        todos.append({
            "content": "Validate implementation",
            "status": "pending",
            "activeForm": "Validating implementation"
        })
        
        return todos
    
    @staticmethod
    def calculate_progress(todos: List[Todo]) -> Dict:
        """Calculate progress metrics from todos"""
        total = len(todos)
        completed = sum(1 for t in todos if t.is_completed)
        in_progress = sum(1 for t in todos if t.is_in_progress)
        pending = total - completed - in_progress
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": (completed / total * 100) if total > 0 else 0,
            "current": next((t.content for t in todos if t.is_in_progress), None)
        }
    
    @staticmethod
    def diff(old_todos: List[Dict], new_todos: List[Dict]) -> List[Dict]:
        """Find changes between todo states"""
        changes = []
        
        old_map = {t["content"]: t["status"] for t in old_todos}
        new_map = {t["content"]: t["status"] for t in new_todos}
        
        for content, new_status in new_map.items():
            old_status = old_map.get(content)
            if old_status != new_status:
                changes.append({
                    "content": content,
                    "old_status": old_status,
                    "new_status": new_status,
                    "action": f"{old_status} -> {new_status}"
                })
        
        return changes
```

### Hook Integration Helper
```python
# claude_parser/domains/todo_hook.py
class TodoHookHelper:
    """Helper for PostToolUse:TodoWrite hook integration"""
    
    @staticmethod
    def parse_hook_data(stdin_data: str) -> Dict:
        """Parse data from PostToolUse hook"""
        # Handle different formats Claude might send
        try:
            return orjson.loads(stdin_data)
        except:
            # Fallback parsing
            return {"todos": [], "error": "Parse failed"}
    
    @staticmethod
    def format_response(success: bool, message: str) -> str:
        """Format response for hook"""
        return orjson.dumps({
            "success": success,
            "message": message,
            "timestamp": pendulum.now().isoformat()
        }).decode()
```

## 🎬 Usage Example

### In task-enforcer
```python
from claude_parser.domains.todo import TodoDomain, TodoHookHelper

class TaskOrchestrator:
    def create_task_with_todos(self, description: str):
        # Create task with context
        task = self.create_context_aware_task(description)
        
        # Generate todos using claude-parser
        todos = TodoDomain.generate_todos(
            task_description=description,
            context={
                "requires_research": task.needs_research,
                "tdd_required": task.needs_tests,
                "complexity": task.complexity
            }
        )
        
        # Return for Claude to use
        return {
            "task_id": task.id,
            "todos": todos,
            "instruction": "Use TodoWrite with these todos"
        }
    
    def handle_todo_update(self, hook_data: str):
        # Parse using claude-parser
        todos = TodoDomain.parse(hook_data)
        
        # Calculate progress
        progress = TodoDomain.calculate_progress(todos)
        
        # Update task
        self.update_task_progress(progress)
```

### In user's hook
```python
#!/usr/bin/env python3
# ~/.claude/hooks/PostToolUse.TodoWrite

import sys
from claude_parser.domains.todo import TodoDomain, TodoHookHelper

def main():
    # Parse hook input
    data = TodoHookHelper.parse_hook_data(sys.stdin.read())
    
    # Parse todos
    todos = TodoDomain.parse(orjson.dumps(data))
    
    # Calculate progress
    progress = TodoDomain.calculate_progress(todos)
    
    # Send to task-enforcer
    response = update_task_system(progress)
    
    # Format response
    print(TodoHookHelper.format_response(True, f"Updated: {progress}"))

if __name__ == "__main__":
    main()
```

## 🎯 Benefits

1. **Reusable** - Any project can use TodoDomain for parsing
2. **Type-safe** - Pydantic models ensure correctness
3. **Testable** - Pure functions, easy to test
4. **Extensible** - Easy to add new todo types/states
5. **Hook-ready** - Designed for PostToolUse integration

## 📅 Implementation Timeline

- **Week 1**: Basic TodoDomain with parse/generate
- **Week 2**: Progress tracking and diff functionality
- **Week 3**: Hook helpers and integration examples
- **Week 4**: Testing and documentation

---

**This domain will enable seamless integration between Claude's TodoWrite tool and any task management system!**