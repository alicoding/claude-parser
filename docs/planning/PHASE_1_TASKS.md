# PHASE 1: Foundation - Detailed Task Breakdown

## Goal
Create the minimal working parser that can load Claude Code JSONL and access messages.

## Success Criteria (MUST PASS)
```python
from claude_parser import load
conv = load("session.jsonl")
print(len(conv.messages))  # Works
print(conv.session_id)      # Works
print(conv.messages[0])     # Works
```

## Task List (In Order)

### TASK 1.1: Project Setup
**Time**: 1 hour
**Files**: pyproject.toml, .gitignore, README.md

**Actions**:
```bash
poetry new claude-parser --name claude_parser
cd claude-parser
poetry add orjson pydantic pendulum loguru rich
poetry add --dev pytest pytest-cov mypy ruff
```

**Success**: `poetry install` completes, `pytest` runs

---

### TASK 1.2: Message Models
**Time**: 2 hours
**File**: claude_parser/models.py

**Implementation**:
```python
from pydantic import BaseModel
from pendulum import DateTime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SUMMARY = "summary"
    SYSTEM = "system"

class Message(BaseModel):
    type: MessageType
    content: str | dict | None
    timestamp: DateTime | None
    uuid: str | None
    session_id: str | None
    parent_uuid: str | None
    
class ToolUse(Message):
    tool_use_id: str
    name: str
    parameters: dict
    
class Summary(BaseModel):
    type: MessageType = MessageType.SUMMARY
    summary: str
    leaf_uuid: str
```

**Tests** (test_models.py):
```python
def test_message_creation():
    msg = Message(type="user", content="Hello")
    assert msg.type == MessageType.USER
    
def test_tool_use_creation():
    tool = ToolUse(
        type="tool_use",
        tool_use_id="123",
        name="Edit",
        parameters={"file": "test.py"}
    )
    assert tool.name == "Edit"
```

**Success**: All model tests pass

---

### TASK 1.3: JSONL Parser
**Time**: 2 hours
**File**: claude_parser/parser.py

**Implementation**:
```python
import orjson
from pathlib import Path
from typing import List
from .models import Message, MessageType

def parse_jsonl(filepath: str | Path) -> List[dict]:
    """Parse JSONL file using orjson."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    messages = []
    with open(filepath, 'rb') as f:
        for line in f:
            if line.strip():
                try:
                    data = orjson.loads(line)
                    messages.append(data)
                except Exception as e:
                    # Log but continue
                    loguru.warning(f"Failed to parse line: {e}")
    
    return messages
```

**Tests** (test_parser.py):
```python
def test_parse_valid_jsonl(tmp_path):
    file = tmp_path / "test.jsonl"
    file.write_text('{"type":"user","content":"Hi"}\n')
    messages = parse_jsonl(file)
    assert len(messages) == 1
    assert messages[0]["type"] == "user"

def test_parse_empty_file(tmp_path):
    file = tmp_path / "empty.jsonl"
    file.touch()
    messages = parse_jsonl(file)
    assert messages == []
```

**Success**: Parser tests pass

---

### TASK 1.4: Conversation Class
**Time**: 3 hours
**File**: claude_parser/conversation.py

**Implementation**:
```python
from typing import List, Optional
from .parser import parse_jsonl
from .models import Message, MessageType

class Conversation:
    """Represents a Claude conversation from JSONL."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._raw_messages = parse_jsonl(filepath)
        self._messages = self._parse_messages()
        self._session_id = self._extract_session_id()
    
    def _parse_messages(self) -> List[Message]:
        """Convert raw dicts to Message objects."""
        messages = []
        for raw in self._raw_messages:
            try:
                msg = Message(**raw)
                messages.append(msg)
            except Exception:
                # Skip malformed messages
                pass
        return messages
    
    def _extract_session_id(self) -> Optional[str]:
        """Extract session ID from messages."""
        for msg in self._messages:
            if msg.session_id:
                return msg.session_id
        return None
    
    @property
    def messages(self) -> List[Message]:
        return self._messages
    
    @property
    def session_id(self) -> Optional[str]:
        return self._session_id
    
    @property
    def assistant_messages(self) -> List[Message]:
        return [m for m in self._messages if m.type == MessageType.ASSISTANT]
    
    @property
    def user_messages(self) -> List[Message]:
        return [m for m in self._messages if m.type == MessageType.USER]
    
    def __len__(self) -> int:
        return len(self._messages)
    
    def __getitem__(self, index):
        return self._messages[index]
```

**Tests** (test_conversation.py):
```python
def test_conversation_load(sample_jsonl):
    conv = Conversation(sample_jsonl)
    assert len(conv) > 0
    assert conv.session_id is not None
    assert isinstance(conv.messages, list)

def test_conversation_properties(sample_jsonl):
    conv = Conversation(sample_jsonl)
    assert len(conv.assistant_messages) >= 0
    assert len(conv.user_messages) >= 0
    assert conv[0] == conv.messages[0]
```

**Success**: Conversation tests pass

---

### TASK 1.5: Public API
**Time**: 1 hour
**File**: claude_parser/__init__.py

**Implementation**:
```python
"""Claude Parser - Parse Claude Code JSONL files with ease."""

from .conversation import Conversation
from .models import Message, MessageType

def load(filepath: str) -> Conversation:
    """Load a Claude conversation from JSONL file.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Conversation object with messages
        
    Example:
        >>> conv = load("session.jsonl")
        >>> print(len(conv.messages))
    """
    return Conversation(filepath)

__all__ = ["load", "Conversation", "Message", "MessageType"]
__version__ = "0.1.0"
```

**Tests** (test_api.py):
```python
def test_load_function():
    from claude_parser import load
    conv = load("test.jsonl")
    assert conv is not None

def test_95_percent_use_case():
    # This MUST work with zero configuration
    from claude_parser import load
    conv = load("real_session.jsonl")
    print(conv.messages)  # Must work
    print(conv.session_id)  # Must work
```

**Success**: Public API test passes

---

### TASK 1.6: Integration Test
**Time**: 1 hour
**File**: tests/test_integration.py

**Test with REAL Claude JSONL**:
```python
def test_real_claude_export():
    """Test with actual Claude Code export."""
    conv = load("fixtures/real_claude.jsonl")
    
    # Verify basic properties
    assert len(conv) > 0
    assert conv.session_id
    
    # Verify message types
    types = {msg.type for msg in conv.messages}
    assert MessageType.USER in types
    
    # Verify 95% use case
    assert conv.messages  # Simple access works
    assert conv.assistant_messages  # Filtering works
```

**Success**: Works with real Claude exports

---

## Definition of Done - Phase 1

### Must Complete:
- [x] Project setup with poetry
- [x] All models defined with pydantic
- [x] Parser using orjson
- [x] Conversation class
- [x] Public API (load function)
- [x] All tests passing
- [x] Works with real Claude JSONL

### Must NOT Include:
- ❌ Async support
- ❌ Streaming
- ❌ Complex queries
- ❌ Export functions
- ❌ File watching

## Verification Command
```bash
# Run this to verify Phase 1 complete
poetry install
poetry run pytest
poetry run mypy claude_parser
poetry run ruff check

# The one-line test
python -c "from claude_parser import load; c=load('test.jsonl'); print(len(c.messages))"
```

## Next Session Handoff
If Phase 1 incomplete, the next session should:
1. Run verification command
2. Fix any failing tests
3. Ensure the one-line API works
4. Move to Phase 2 ONLY when all Phase 1 tests pass

---
*This is the COMPLETE Phase 1 scope. Nothing more, nothing less.*