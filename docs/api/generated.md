## Public CLI Commands:

### `cg_reflog.py`
- `show(uuid: str)`: Show details of a specific message (like git show)
- `reflog(limit: int)`: Show all operations history (like git reflog)

### `cg_basic.py`
- `status()`: Show current session and project status
- `log(limit: int)`: Show message history

### `cg_advanced.py`
- `find(pattern: str)`: Find files in any message (like git log --all --grep)
- `blame()`: Show file history

## Public SDK Functions:

### `core.py`
- `estimate_cost(total_tokens: int, model: str) -> float`: Estimate API cost using configured prices

## Public API Endpoints:

### `api.py`
- `parse_hook_input() -> Dict[str, Any]`: Parse hook input from stdin
- `allow_operation(reason: str)`: Allow the operation (PreToolUse)
- `block_operation(reason: str)`: Block the operation (PreToolUse/PostToolUse/Stop)
- `request_approval(reason: str)`: Request user approval (PreToolUse)
- `add_context(text: str)`: Add context for Claude (UserPromptSubmit/SessionStart)
- `execute_hook(plugin_callback: Callable) -> None`: Execute hook with plugin callback

## MCP Tool Functions:

- No MCP tool functions were found in the provided files.

This documentation provides a clear overview of the user-facing interfaces in the Claude Parser project, including CLI commands, SDK functions, API endpoints, and MCP tool functions.