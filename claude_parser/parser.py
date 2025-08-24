"""
JSONL parser using orjson for 10x performance.
"""

import orjson
from pathlib import Path
from typing import List, Dict, Any, Iterator, Tuple
from loguru import logger


def parse_jsonl(filepath: str | Path) -> List[Dict[str, Any]]:
    """Parse JSONL file using orjson.
    
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
    
    messages = []
    errors = []
    
    with open(filepath, 'rb') as f:
        for line_num, line in enumerate(f, 1):
            # Skip empty lines
            if not line.strip():
                continue
            
            try:
                # orjson returns bytes, loads returns Python objects
                data = orjson.loads(line)
                messages.append(data)
            except orjson.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: Failed to parse JSON - {e}")
                errors.append((line_num, str(e)))
                # Continue parsing rest of file
                continue
    
    if errors:
        logger.info(f"Parsed {len(messages)} messages, skipped {len(errors)} malformed lines")
    
    return messages


def parse_jsonl_streaming(filepath: str | Path) -> Iterator[Dict[str, Any]]:
    """Parse JSONL file with streaming (memory efficient).
    
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
        for line_num, line in enumerate(f, 1):
            # Skip empty lines
            if not line.strip():
                continue
            
            try:
                data = orjson.loads(line)
                yield data
            except orjson.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: Failed to parse JSON - {e}")
                # Skip malformed lines
                continue


def count_messages(filepath: str | Path) -> int:
    """Count messages in JSONL file without loading all into memory.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Number of valid JSON messages
    """
    count = 0
    for _ in parse_jsonl_streaming(filepath):
        count += 1
    return count


def validate_jsonl(filepath: str | Path) -> tuple[bool, List[int]]:
    """Validate JSONL file structure.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        Tuple of (is_valid, list_of_error_line_numbers)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    error_lines = []
    
    with open(filepath, 'rb') as f:
        for line_num, line in enumerate(f, 1):
            # Skip empty lines
            if not line.strip():
                continue
            
            try:
                orjson.loads(line)
            except orjson.JSONDecodeError:
                error_lines.append(line_num)
    
    return len(error_lines) == 0, error_lines


def validate_claude_format(filepath: str | Path) -> Tuple[bool, List[str]]:
    """Validate that JSONL file follows Claude Code format.
    
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
    
    errors = []
    messages = []
    
    # Load first 20 messages to check format (more comprehensive sample)
    try:
        for i, msg in enumerate(parse_jsonl_streaming(filepath)):
            messages.append(msg)
            if i >= 19:  # Check first 20 messages
                break
    except Exception as e:
        return False, [f"Failed to parse JSONL: {e}"]
    
    if len(messages) == 0:
        return False, ["File is empty or contains no valid messages"]
    
    # Define Claude format signatures
    claude_signatures = [
        "sessionId",     # Most Claude messages have session IDs
        "leafUuid",      # Summary messages have this
        "gitBranch",     # Claude Code exports include git info
        "cwd",           # Claude Code exports include working directory
        "toolUseID",     # Tool use messages
        "isSidechain",   # Claude conversation metadata
        "userType"       # Claude user type info
    ]
    
    # Define Claude message types
    claude_message_types = [
        "user", "assistant", "tool_use", "tool_result", 
        "summary", "system"
    ]
    
    # Check for Claude signatures
    signature_count = 0
    claude_type_count = 0
    
    for msg in messages:
        # Count Claude-specific signatures
        for signature in claude_signatures:
            if signature in msg:
                signature_count += 1
                break  # Only count once per message
        
        # Count Claude message types
        msg_type = msg.get("type", "")
        if msg_type in claude_message_types:
            claude_type_count += 1
    
    # Validation criteria
    signature_ratio = signature_count / len(messages) if messages else 0
    type_ratio = claude_type_count / len(messages) if messages else 0
    
    # At least 70% of messages should have Claude signatures
    if signature_ratio < 0.7:
        errors.append(f"Low Claude signature ratio: {signature_ratio:.2f} (expected >= 0.7)")
    
    # At least 80% should have valid Claude message types
    if type_ratio < 0.8:
        errors.append(f"Low Claude message type ratio: {type_ratio:.2f} (expected >= 0.8)")
    
    # Check for session consistency (if sessionId exists) - but be more lenient
    session_ids = set()
    for msg in messages:
        if "sessionId" in msg:
            session_ids.add(msg["sessionId"])
    
    # Only require sessionId if we have many Claude signatures
    if len(session_ids) == 0 and signature_ratio > 0.8:
        errors.append("High Claude signature ratio but no sessionId found")
    
    is_valid = len(errors) == 0
    return is_valid, errors