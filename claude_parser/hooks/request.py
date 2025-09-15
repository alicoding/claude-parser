#!/usr/bin/env python3
"""
HookRequest - Clean data encapsulation for hook requests
@UTIL_FIRST: Delegates to existing utils
@LOC_ENFORCEMENT: <80 LOC
"""

from typing import List, Tuple, Optional, Any, Dict
from .utils import read_stdin, write_output
from .aggregator import aggregate_results


class HookRequest:
    """Encapsulates hook request data and response handling"""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize from parsed hook data - handles both camelCase and snake_case"""
        self.data = data

        # Handle both formats (Claude Code sends camelCase)
        self.session_id = data.get("session_id") or data.get("sessionId", "")
        self.transcript_path = data.get("transcript_path") or data.get("transcriptPath", "")
        self.cwd = data.get("cwd", "")
        self.hook_event_name = data.get("hook_event_name") or data.get("hookEventName", "")

        # Tool-specific fields
        self.tool_name = data.get("tool_name") or data.get("toolName")
        self.tool_input = data.get("tool_input") or data.get("toolInput", {})
        self.tool_response = data.get("tool_response") or data.get("toolResponse")
        
        # Other hook-specific fields
        self.prompt = data.get("prompt")
        self.message = data.get("message")
        self.reason = data.get("reason")
        self.source = data.get("source")
        
        # Lazy-load conversation
        self._conversation = None
    
    
    @property
    def conversation(self):
        """Lazy-load conversation when needed"""
        if self._conversation is None and self.transcript_path:
            try:
                from ..main import load_session
                self._conversation = load_session(self.transcript_path)
            except:
                self._conversation = None
        return self._conversation

    def get_latest_claude_message(self):
        """Get Claude's latest message - @UTIL_FIRST delegation

        100% framework delegation to existing navigation utilities.
        """
        if not self.conversation:
            return None

        # Delegate to existing navigation utility
        from ..navigation.core import get_latest_assistant_message
        messages = self.conversation.get('messages', [])
        return get_latest_assistant_message(messages)

    def complete(self, results: List[Tuple[str, Optional[str]]]) -> int:
        """Aggregate results and output, return exit code

        @ANY_BLOCK_WINS: If any plugin blocks, whole operation fails
        """
        # Delegate aggregation to specialized module
        output, exit_code = aggregate_results(self.hook_event_name, results)

        # Output JSON to stdout (hooks always output JSON)
        if output is not None:
            import sys
            print(output, file=sys.stdout)

        return exit_code