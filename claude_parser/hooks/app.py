#!/usr/bin/env python3
"""
Claude Parser Hooks - 100% Typer Framework Delegation
LNCA compliant: <80 LOC, single responsibility (CLI interface only)

Typer handles ALL concerns:
- Type safety (automatic via type hints)
- JSON parsing (built-in option parsing) 
- Rich output (built-in Rich integration)
- Hook routing (callback system)
- Exit codes (built-in)
- Validation (automatic)
"""

import typer
from typing import Optional
from .models import HookEvent, parse_hook_context
from .handlers import route_hook_event

app = typer.Typer(
    name="claude-hooks",
    help="Superior hook system with 100% Typer delegation",
    no_args_is_help=False,
    invoke_without_command=True
)

@app.callback()
def process_hook(
    ctx: typer.Context,
    # Core hook data - Typer handles ALL parsing & validation
    hook_event_name: HookEvent = typer.Option(..., help="Hook event type"),
    session_id: str = typer.Option(..., help="Session identifier"),
    transcript_path: str = typer.Option(..., help="Path to transcript"),
    cwd: str = typer.Option(..., help="Current working directory"),
    
    # Optional fields based on hook type - Typer handles type safety
    tool_name: Optional[str] = typer.Option(None, help="Tool name for tool hooks"),
    tool_input: Optional[str] = typer.Option(None, help="Tool input JSON"),
    tool_response: Optional[str] = typer.Option(None, help="Tool response JSON"),
    prompt: Optional[str] = typer.Option(None, help="User prompt text"),
    message: Optional[str] = typer.Option(None, help="Message content"),
    source: Optional[str] = typer.Option(None, help="Session start source"),
):
    """
    100% Typer delegation hook processor
    
    Typer automatically handles:
    - Type validation of all parameters
    - Rich error messages and help
    - JSON parsing (when needed)
    - Exit code management
    - Command routing
    """
    
    # Parse context - Typer handles validation
    context = parse_hook_context(
        hook_event_name=hook_event_name,
        session_id=session_id,
        transcript_path=transcript_path,
        cwd=cwd,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_response=tool_response,
        prompt=prompt,
        message=message,
        source=source
    )
    
    # Route to handler - framework does everything
    route_hook_event(**context)

if __name__ == "__main__":
    app()