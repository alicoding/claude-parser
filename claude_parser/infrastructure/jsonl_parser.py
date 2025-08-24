"""
JSONL parsing infrastructure using functional programming.

95/5 Principle:
- Uses orjson for fast parsing
- Uses toolz/more-itertools for functional operations
- NO manual loops, NO manual state management
"""

import orjson
from pathlib import Path
from typing import List, Dict, Any, Iterator, Tuple, Optional
from loguru import logger
from toolz import (
    filter as toolz_filter,
    map as toolz_map,
    partition,
    pipe,
    compose,
    reduce,
)
from more_itertools import partition as more_partition, ilen


def parse_line_safe(indexed_line: Tuple[int, bytes]) -> Optional[Tuple[str, Any]]:
    """Parse a single line, returning tagged result.
    
    Returns:
        None if empty line
        ('success', data) if parsed successfully  
        ('error', (line_num, error_msg)) if failed
    """
    line_num, line = indexed_line
    if not line.strip():
        return None
    
    try:
        return ('success', orjson.loads(line))
    except orjson.JSONDecodeError as e:
        logger.warning(f"Line {line_num}: Failed to parse JSON - {e}")
        return ('error', (line_num, str(e)))


def parse_jsonl(filepath: str | Path) -> List[Dict[str, Any]]:
    """Parse JSONL file using functional approach.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        List of parsed JSON objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        # Functional pipeline: enumerate → parse → filter None → partition
        results = list(
            toolz_filter(
                lambda x: x is not None,
                toolz_map(parse_line_safe, enumerate(f, 1))
            )
        )
    
    # Partition into errors and successes functionally
    errors = list(toolz_filter(lambda x: x[0] == 'error', results))
    successes = list(toolz_filter(lambda x: x[0] == 'success', results))
    
    # Extract actual data from tagged tuples
    messages = list(toolz_map(lambda x: x[1], successes))
    error_details = list(toolz_map(lambda x: x[1], errors))
    
    if error_details:
        logger.info(f"Parsed {len(messages)} messages, skipped {len(error_details)} malformed lines")
    
    return messages


def parse_jsonl_streaming(filepath: str | Path) -> Iterator[Dict[str, Any]]:
    """Parse JSONL file with streaming (memory efficient).
    
    Uses functional generators for lazy evaluation.
    
    Args:
        filepath: Path to JSONL file
        
    Yields:
        Parsed JSON objects one at a time
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        # Create functional pipeline for streaming
        parsed_lines = toolz_map(parse_line_safe, enumerate(f, 1))
        filtered_results = toolz_filter(lambda x: x is not None, parsed_lines)
        successful_results = toolz_filter(lambda x: x[0] == 'success', filtered_results)
        extracted_data = toolz_map(lambda x: x[1], successful_results)
        
        # Yield results from the pipeline
        yield from extracted_data


def count_messages(filepath: str | Path) -> int:
    """Count messages in JSONL file without loading all into memory.
    
    Uses functional approach with ilen for counting.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Number of valid JSON messages
    """
    # Use ilen for functional counting
    return ilen(parse_jsonl_streaming(filepath))


def validate_jsonl(filepath: str | Path) -> Tuple[bool, List[int]]:
    """Validate JSONL file structure functionally.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Tuple of (is_valid, list_of_error_line_numbers)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        # Parse all lines and collect errors
        results = list(
            toolz_filter(
                lambda x: x is not None,
                toolz_map(parse_line_safe, enumerate(f, 1))
            )
        )
    
    # Extract error line numbers functionally
    error_lines = list(
        toolz_map(
            lambda x: x[1][0],  # Extract line number from error tuple
            toolz_filter(lambda x: x[0] == 'error', results)
        )
    )
    
    return len(error_lines) == 0, error_lines


def validate_claude_format(filepath: str | Path) -> Tuple[bool, List[str]]:
    """Validate that JSONL file follows Claude Code format.
    
    Uses functional approach for validation.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False, [f"File not found: {filepath}"]
    
    # First check if it's valid JSONL
    is_valid_jsonl, error_lines = validate_jsonl(filepath)
    if not is_valid_jsonl:
        return False, [f"Invalid JSONL format. Errors on lines: {error_lines}"]
    
    # Load first 20 messages for validation using streaming
    messages = list(pipe(
        parse_jsonl_streaming(filepath),
        lambda msgs: toolz_map(lambda x: x[1] if isinstance(x, tuple) else x, msgs),
        lambda msgs: list(msgs)[:20]  # Take first 20
    ))
    
    if not messages:
        return False, ["File is empty or contains no valid messages"]
    
    # Define Claude format signatures
    claude_signatures = [
        "sessionId", "leafUuid", "gitBranch", "cwd",
        "toolUseID", "isSidechain", "userType"
    ]
    
    # Define Claude message types
    claude_message_types = [
        "user", "assistant", "tool_use", "tool_result", 
        "summary", "system"
    ]
    
    # Check signatures functionally
    def has_claude_signature(msg):
        return pipe(
            claude_signatures,
            lambda sigs: toolz_map(lambda sig: sig in msg, sigs),
            any
        )
    
    def has_claude_type(msg):
        return msg.get("type", "") in claude_message_types
    
    # Count using functional approach
    signature_count = len(list(toolz_filter(has_claude_signature, messages)))
    type_count = len(list(toolz_filter(has_claude_type, messages)))
    
    # Calculate ratios
    total = len(messages)
    signature_ratio = signature_count / total if total else 0
    type_ratio = type_count / total if total else 0
    
    # Check for session consistency functionally
    session_ids = set(
        toolz_filter(
            None,
            toolz_map(lambda msg: msg.get("sessionId"), messages)
        )
    )
    
    # Build validation errors functionally
    error_checks = [
        (signature_ratio < 0.7, 
         f"Low Claude signature ratio: {signature_ratio:.2f} (expected >= 0.7)"),
        (type_ratio < 0.8,
         f"Low Claude message type ratio: {type_ratio:.2f} (expected >= 0.8)"),
        (not session_ids and signature_ratio > 0.8,
         "High Claude signature ratio but no sessionId found"),
    ]
    
    # Filter to get only actual errors
    errors = list(
        toolz_map(
            lambda x: x[1],
            toolz_filter(lambda x: x[0], error_checks)
        )
    )
    
    return len(errors) == 0, errors