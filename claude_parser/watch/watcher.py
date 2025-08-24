"""Watch domain implementation following 95/5 principle.

Single Responsibility: File watching with incremental parsing.
Uses watchfiles library for cross-platform file monitoring.
"""

from typing import Callable, Optional, List, Set
from pathlib import Path
import sys
from toolz import filter as toolz_filter, map as toolz_map
from more_itertools import consume

try:
    import watchfiles
except ImportError:
    print("watchfiles library required. Install with: pip install watchfiles", file=sys.stderr)
    sys.exit(1)

from ..models.base import Message
from ..domain.entities.conversation import Conversation
from .. import load


class IncrementalReader:
    """Single Responsibility: Track file reading position."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.last_position = 0
        self.last_inode = None
    
    def get_new_lines(self) -> List[str]:
        """Read only new lines since last read."""
        try:
            stat = self.file_path.stat()
            current_inode = stat.st_ino
            
            # Handle file rotation (inode changed)
            if self.last_inode is not None and current_inode != self.last_inode:
                self.last_position = 0
            
            self.last_inode = current_inode
            
            # Handle file truncation (size < position)
            if stat.st_size < self.last_position:
                self.last_position = 0
            
            # Read new content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
            
            # Use functional approach instead of list comprehension
            from operator import methodcaller
            stripped_lines = toolz_map(methodcaller('strip'), new_lines)
            return list(toolz_filter(bool, stripped_lines))
            
        except (FileNotFoundError, PermissionError):
            return []


def watch(file_path: str, 
          callback: Callable[[Conversation, List[Message]], None],
          message_types: Optional[List[str]] = None) -> None:
    """
    Watch JSONL file for changes and call callback with new messages.
    
    Args:
        file_path: Path to JSONL file
        callback: Function called with (full_conversation, new_messages)
        message_types: Optional filter ["user", "assistant", "tool_use", etc.]
    
    Example (95% use case):
        def on_new(conv, new_msgs):
            print(f"Got {len(new_msgs)} new messages")
        
        watch("session.jsonl", on_new)  # Blocks, monitors forever
    """
    file_path = str(Path(file_path).resolve())
    
    # Verify file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    reader = IncrementalReader(file_path)
    message_type_filter: Optional[Set[str]] = set(message_types) if message_types else None
    
    # Process initial file state (don't trigger callback for existing content)
    reader.get_new_lines()  # Advance position to end
    
    # Define processing function for each change set
    from functools import partial
    process_fn = partial(
        _process_file_changes,
        file_path=file_path,
        reader=reader,
        message_type_filter=message_type_filter,
        callback=callback
    )
    
    try:
        # Consume infinite generator functionally using more_itertools.consume
        # This replaces the for loop with functional approach
        consume(toolz_map(process_fn, watchfiles.watch(file_path)))
                        
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        pass
    except Exception as e:
        print(f"Watch error: {e}", file=sys.stderr)
        raise


def _process_file_changes(changes, file_path: str, reader, message_type_filter, callback):
    """Process file changes functionally."""
    # Filter changes to only our target file
    relevant_changes = toolz_filter(
        lambda change: change[1] == file_path,
        changes
    )
    
    # Process if we have relevant changes
    if any(relevant_changes):
        new_lines = reader.get_new_lines()
        
        if new_lines:
            new_messages = _parse_new_messages(new_lines, message_type_filter)
            
            if new_messages:
                full_conversation = load(file_path)
                callback(full_conversation, new_messages)


def _parse_new_messages(lines: List[str], message_type_filter: Optional[Set[str]]) -> List[Message]:
    """Parse new JSONL lines into Message objects."""
    import orjson
    from ..models import parse_message
    
    def parse_line_safe(line):
        """Parse a line safely, return message or None."""
        try:
            raw_data = orjson.loads(line)
            message = parse_message(raw_data)
            
            # Apply message type filter if specified
            if message_type_filter is None or message.type in message_type_filter:
                return message
            return None
                
        except Exception as e:
            # Log parsing error but don't crash watcher
            print(f"Failed to parse message: {e}", file=sys.stderr)
            return None
    
    # Use functional approach instead of manual loops
    parsed_messages = toolz_map(parse_line_safe, lines)
    valid_messages = toolz_filter(lambda msg: msg is not None, parsed_messages)
    
    return list(valid_messages)