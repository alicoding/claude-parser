"""TodoManager - Facade for todo operations.

Orchestrates Parser, Storage, and Display (DDD).
"""
from typing import List, Dict, Optional, Union
from rich.console import Console
from rich.progress import Progress

from .parser import TodoParser
from .storage import TodoStorage
from .display import TodoDisplay


class TodoManager:
    """Facade for todo operations. Delegates to specialized classes."""
    
    def __init__(self, session_id: str, agent_id: Optional[str] = None):
        """Initialize with session and agent IDs.
        
        Args:
            session_id: Session UUID from transcript
            agent_id: Agent UUID (defaults to session_id)
        """
        # Composition over inheritance (SOLID)
        self.storage = TodoStorage(session_id, agent_id)
        self.console = Console()
    
    def read(self) -> List[Dict]:
        """Read todos from storage."""
        return self.storage.read()
    
    def write(self, todos: List[Dict]) -> str:
        """Write todos to storage."""
        return self.storage.write(todos)
    
    def delete(self) -> bool:
        """Delete todo file."""
        return self.storage.delete()
    
    def display(self, show_progress: bool = True):
        """Display todos using Rich.
        
        Args:
            show_progress: Whether to show progress bar
        """
        todos = self.read()
        
        # Build and display tree (Rich does the work)
        tree = TodoDisplay.build_tree(todos)
        self.console.print(tree)
        
        # Show progress if requested
        if show_progress and todos:
            progress = TodoDisplay.calculate_progress(todos)
            
            # Rich Progress bar (95% library)
            with Progress() as p:
                task = p.add_task(
                    f"[cyan]Progress",
                    total=progress["total"]
                )
                p.update(task, completed=progress["completed"])
    
    @staticmethod
    def parse(data: Union[str, bytes]) -> List[Dict]:
        """Parse todos from JSON.
        
        Delegates to TodoParser (Single Responsibility).
        """
        return TodoParser.parse(data)
    
    @staticmethod
    def calculate_progress(todos: List[Dict]) -> Dict:
        """Calculate progress metrics.
        
        Delegates to TodoDisplay (Single Responsibility).
        """
        return TodoDisplay.calculate_progress(todos)