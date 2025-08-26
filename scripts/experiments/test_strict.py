#!/usr/bin/env python3
"""Test strict validation."""

from pathlib import Path
from claude_parser import load

# Create test file like the test does
test_file = Path("test_invalid.jsonl")
invalid_content = [
    '{"type": "user", "message": "Hello"}',  # Missing Claude fields
    '{"type": "random", "data": "Unknown message type"}'
]
test_file.write_text('\n'.join(invalid_content))

try:
    conv = load(test_file, strict=True)
    print(f"Loaded without error: {len(conv)} messages")
except ValueError as e:
    print(f"Raised ValueError as expected: {e}")
    
# Check what validate_claude_format returns
from claude_parser.parser import validate_claude_format
is_valid, errors = validate_claude_format(test_file)
print(f"Is valid: {is_valid}")
print(f"Errors: {errors}")

# Cleanup
test_file.unlink()
