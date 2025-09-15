# USER GUIDE: Claude Parser Tool

## CLI Commands:
1. **Show Message History:**
   - Command: `cg_basic log`
   - Description: Displays the message history from the current session.
   - Example: `cg_basic log --limit 10`

2. **Show Specific Message Details:**
   - Command: `cg_reflog show <uuid>`
   - Description: Shows details of a specific message using its UUID.
   - Example: `cg_reflog show abc123`

3. **Show Operations History:**
   - Command: `cg_reflog reflog`
   - Description: Displays all operations history across sessions.
   - Example: `cg_reflog reflog --limit 20`

## Calling SDK from Python Code:
1. **Analyzing Tool Usage:**
   - Function: `analyze_tool_usage(session_data: Dict[str, Any]) -> Dict[str, Any]`
   - Description: Analyzes tool usage from session data.
   - Example: `analyze_tool_usage(session_data)`

2. **Calculating Session Cost:**
   - Function: `calculate_session_cost(...) -> Dict[str, float]`
   - Description: Calculates session cost based on token usage.
   - Example: `calculate_session_cost(input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, model)`

3. **Calculating Context Window:**
   - Function: `calculate_context_window(jsonl_path: Optional[str] = None) -> Dict[str, int]`
   - Description: Calculates context window usage with user/assistant separation.
   - Example: `calculate_context_window(jsonl_path)`

## Integrating with MCP Tools in Claude:
- The tool provides functions to analyze tool usage, calculate session cost, and estimate token usage.
- These functions can be integrated with other MCP tools in Claude for comprehensive analytics and billing.

## Common Workflows and Use Cases:
1. **Analyzing Tool Usage:**
   - Use the `analyze_tool_usage` function to track tool usage patterns in sessions.
2. **Calculating Session Cost:**
   - Utilize the `calculate_session_cost` function to estimate the cost of a session based on token usage.
3. **Monitoring Context Window Usage:**
   - Use the `calculate_context_window` function to monitor and manage context window token usage.

By following the provided CLI commands and SDK functions, users can effectively analyze tool usage, calculate session costs, and integrate with other MCP tools in Claude for enhanced analytics and workflows.