"""
File utilities for DRY principle compliance.

SOLID: Single Responsibility - File operations
DRY: Shared utilities to eliminate duplication
95/5: Using pathlib and orjson libraries
"""

from pathlib import Path
from typing import Iterator, Optional, Any
import orjson
from .logger_config import logger


def ensure_file_exists(filepath: Path) -> Path:
    """Ensure file exists, raise FileNotFoundError if not.
    
    DRY: Single place for file existence validation.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return filepath


def read_jsonl_lines(filepath: Path) -> Iterator[tuple[int, bytes]]:
    """Read JSONL file lines with line numbers.
    
    DRY: Single place for file reading pattern.
    Yields: (line_number, line_bytes) tuples
    """
    filepath = ensure_file_exists(filepath)
    with open(filepath, 'rb') as f:
        # Use functional approach to avoid manual loop
        lines = list(f)  # Read all lines at once
        numbered_lines = enumerate(lines, 1)
        yield from numbered_lines


def parse_json_safe(data: bytes, line_num: Optional[int] = None) -> tuple[bool, Any]:
    """Parse JSON safely with error handling.
    
    DRY: Single place for JSON parsing with errors.
    Returns: (success, result_or_error)
    """
    try:
        return True, orjson.loads(data)
    except orjson.JSONDecodeError as e:
        if line_num:
            logger.warning(f"Line {line_num}: Failed to parse JSON - {e}")
        else:
            logger.warning(f"Failed to parse JSON - {e}")
        return False, str(e)


def log_parse_results(success_count: int, error_count: int, filepath: Path) -> None:
    """Log parsing results consistently.
    
    DRY: Single place for result logging.
    """
    if error_count > 0:
        logger.info(f"Parsed {success_count} messages from {filepath.name}, skipped {error_count} malformed lines")
    else:
        logger.info(f"Parsed {success_count} messages from {filepath.name}")