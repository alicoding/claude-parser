# Phase 2: Comprehensive Hook Testing Plan

## 🎯 Testing Strategy

### Core Principle: Test with REAL Claude Hook Data
We'll use actual Claude Code hook JSON formats, not mocked data.

### Test Data Sources:
1. **Real JSONL files**: `/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2/jsonl-sample/`
2. **Hook JSON samples**: From official `docs/hooks.md` documentation
3. **Echo testing**: Using `echo '{"json":"data"}' | python hook.py` pattern

---

## 📋 Test Infrastructure (Step 1)

### Fixtures Needed

```python
# tests/test_phase2/conftest.py
import pytest
import json
import sys
import orjson
from io import StringIO
from pathlib import Path

# Real hook JSON samples from Claude Code
HOOK_SAMPLES = {
    "PreToolUse": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/test.txt",
            "content": "test content"
        }
    },
    "PostToolUse": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "tool_response": {"output": "file1.txt\nfile2.txt", "success": True}
    },
    "UserPromptSubmit": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Write a function to calculate factorial"
    },
    "Stop": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "Stop",
        "stop_hook_active": False
    },
    "Notification": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "Notification",
        "message": "Claude needs your permission to use Bash"
    },
    "SessionStart": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "SessionStart",
        "source": "startup"
    },
    "PreCompact": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreCompact",
        "trigger": "manual",
        "custom_instructions": ""
    },
    "SubagentStop": {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "SubagentStop",
        "stop_hook_active": False
    }
}

@pytest.fixture
def mock_stdin():
    """Mock stdin with JSON data."""
    def _mock(data):
        if isinstance(data, dict):
            json_str = orjson.dumps(data).decode()
        else:
            json_str = data
        
        old_stdin = sys.stdin
        sys.stdin = StringIO(json_str)
        yield sys.stdin
        sys.stdin = old_stdin
    return _mock

@pytest.fixture
def capture_exit():
    """Capture sys.exit calls."""
    class ExitCapture:
        def __init__(self):
            self.code = None
            self.called = False
        
        def __call__(self, code=0):
            self.code = code
            self.called = True
            raise SystemExit(code)
    
    return ExitCapture()

@pytest.fixture
def hook_sample():
    """Get hook sample data."""
    def _get(hook_type):
        return HOOK_SAMPLES[hook_type].copy()
    return _get

@pytest.fixture
def real_transcript():
    """Use real JSONL file if available."""
    path = Path("/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2/jsonl-sample/6d0efa65-3f7f-4c79-9b58-1e7a23d57f11.jsonl")
    if path.exists():
        return str(path)
    # Create minimal test file
    test_file = Path("/tmp/test_transcript.jsonl")
    test_file.write_text('{"type":"user","message":{"content":"test"}}\n')
    return str(test_file)
```

---

## 🧪 Test Scenarios

### 1. HookData Model Tests (Step 2)

```python
# tests/test_phase2/test_hook_models.py

def test_single_model_all_hooks(hook_sample):
    """One HookData model handles ALL 8 hook types (DRY)."""
    from claude_parser.hooks.models import HookData
    
    for hook_type in HOOK_SAMPLES.keys():
        data = HookData(**hook_sample(hook_type))
        assert data.hook_event_name == hook_type
        assert data.hook_type == hook_type  # Convenience property
        assert data.session_id == "abc123"

def test_optional_fields():
    """Optional fields work correctly."""
    from claude_parser.hooks.models import HookData
    
    # Minimal required fields
    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse"
    )
    assert data.tool_name is None
    assert data.tool_input is None

def test_immutable():
    """Models are frozen (immutable)."""
    from claude_parser.hooks.models import HookData
    
    data = HookData(**HOOK_SAMPLES["PreToolUse"])
    with pytest.raises(AttributeError):
        data.session_id = "changed"

def test_load_conversation(real_transcript):
    """HookData can load conversation using Phase 1 parser."""
    from claude_parser.hooks.models import HookData
    
    data = HookData(
        session_id="test",
        transcript_path=real_transcript,
        cwd="/test",
        hook_event_name="PreToolUse"
    )
    
    conv = data.load_conversation()
    assert len(conv) > 0
```

### 2. Hook Input Tests (Step 3)

```python
# tests/test_phase2/test_hook_input.py

def test_hook_input_parses_stdin(mock_stdin, hook_sample):
    """hook_input() parses JSON from stdin."""
    from claude_parser.hooks import hook_input
    
    test_data = hook_sample("PreToolUse")
    
    with mock_stdin(test_data):
        data = hook_input()
    
    assert data.session_id == "abc123"
    assert data.tool_name == "Write"

def test_invalid_json(mock_stdin, capsys):
    """Graceful error on invalid JSON."""
    from claude_parser.hooks import hook_input
    
    with mock_stdin("not valid json"):
        with pytest.raises(SystemExit) as exc:
            hook_input()
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.err

def test_missing_required_fields(mock_stdin, capsys):
    """Graceful error on missing required fields."""
    from claude_parser.hooks import hook_input
    
    with mock_stdin({"session_id": "test"}):  # Missing required
        with pytest.raises(SystemExit) as exc:
            hook_input()
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Missing required" in captured.err or "validation error" in captured.err.lower()
```

### 3. Exit Helper Tests (Step 4)

```python
# tests/test_phase2/test_hook_exits.py

def test_exit_success_no_message(capsys):
    """exit_success() exits 0 with optional stdout."""
    from claude_parser.hooks import exit_success
    
    with pytest.raises(SystemExit) as exc:
        exit_success()
    
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

def test_exit_success_with_message(capsys):
    """exit_success() can include stdout message."""
    from claude_parser.hooks import exit_success
    
    with pytest.raises(SystemExit) as exc:
        exit_success("All good")
    
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "All good" in captured.out

def test_exit_block(capsys):
    """exit_block() exits 2 with stderr reason."""
    from claude_parser.hooks import exit_block
    
    with pytest.raises(SystemExit) as exc:
        exit_block("Security violation")
    
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Security violation" in captured.err

def test_exit_error(capsys):
    """exit_error() exits 1 with stderr."""
    from claude_parser.hooks import exit_error
    
    with pytest.raises(SystemExit) as exc:
        exit_error("Warning message")
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Warning message" in captured.err
```

### 4. Integration Tests with Echo

```python
# tests/test_phase2/test_hook_integration.py
import subprocess
import json

def test_echo_pipe_pretooluse():
    """Test real echo piping like Claude Code does."""
    hook_data = {
        "session_id": "test123",
        "transcript_path": "/tmp/test.jsonl",
        "cwd": "/tmp",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/etc/passwd"}
    }
    
    # Create test script
    script = """
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if "passwd" in str(data.tool_input.get("file_path", "")):
    exit_block("Protected file")
exit_success()
"""
    
    # Run with echo pipe
    result = subprocess.run(
        f"echo '{json.dumps(hook_data)}' | python -c '{script}'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 2
    assert "Protected file" in result.stderr

def test_performance():
    """Hook processing < 10ms."""
    import time
    from claude_parser.hooks import hook_input
    
    test_data = HOOK_SAMPLES["PreToolUse"]
    
    start = time.time()
    with mock_stdin(test_data):
        data = hook_input()
    elapsed = time.time() - start
    
    assert elapsed < 0.01  # 10ms
```

### 5. Advanced JSON Output Tests

```python
# tests/test_phase2/test_hook_advanced.py

def test_json_output_pretooluse(capsys):
    """JSON output for PreToolUse uses hookSpecificOutput."""
    from claude_parser.hooks.advanced import json_output
    
    with pytest.raises(SystemExit) as exc:
        json_output(
            hook_type="PreToolUse",
            decision="deny",
            reason="Security"
        )
    
    assert exc.value.code == 0
    output = orjson.loads(capsys.readouterr().out)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

def test_json_output_other_hooks(capsys):
    """JSON output for other hooks uses simple format."""
    from claude_parser.hooks.advanced import json_output
    
    with pytest.raises(SystemExit) as exc:
        json_output(
            hook_type="PostToolUse",
            decision="block",
            reason="Failed"
        )
    
    output = orjson.loads(capsys.readouterr().out)
    assert output["decision"] == "block"
    assert output["reason"] == "Failed"
```

---

## 🔄 Test Execution Plan

### Sequential Order (TDD):
1. **Write failing test first**
2. **Implement minimal code to pass**
3. **Refactor if needed**
4. **Run all tests**

### Commands:
```bash
# Step 1: Create test infrastructure
pytest tests/test_phase2/conftest.py -v

# Step 2: Test models (TDD - write first)
pytest tests/test_phase2/test_hook_models.py -v

# Step 3: Test hook_input
pytest tests/test_phase2/test_hook_input.py -v

# Step 4: Test exit helpers
pytest tests/test_phase2/test_hook_exits.py -v

# Step 5: Test advanced features
pytest tests/test_phase2/test_hook_advanced.py -v

# Step 6: Integration tests
pytest tests/test_phase2/test_hook_integration.py -v

# Full suite
pytest tests/test_phase2/ -v --cov=claude_parser.hooks
```

---

## ✅ Success Criteria

### Coverage:
- 100% test coverage required
- No skipped tests
- All 8 hook types tested

### Performance:
- Hook parsing < 10ms
- Memory usage constant
- No memory leaks

### Quality:
- Tests use real Claude formats
- Echo pipe testing works
- Error cases handled
- Integration with Phase 1 parser works

---

## 🎯 The 95/5 Test

The simplest hook MUST work in 3 lines:
```bash
echo '{"session_id":"abc","transcript_path":"/tmp/t.jsonl","cwd":"/tmp","hook_event_name":"PreToolUse","tool_name":"Write"}' | python -c "
from claude_parser.hooks import hook_input, exit_block, exit_success
data = hook_input()
if data.tool_name == 'Write': exit_block('No writes')
exit_success()
"
```

This should:
1. Parse stdin JSON
2. Check tool name
3. Exit with code 2 and stderr message