#!/usr/bin/env python3
"""Fix test method calls to use properties."""

import re
from pathlib import Path

# Find all test files
test_files = list(Path("tests").rglob("*.py"))

for test_file in test_files:
    content = test_file.read_text()
    original = content
    
    # Replace method calls with property access
    content = re.sub(r'\.assistant_messages\(\)', '.assistant_messages', content)
    content = re.sub(r'\.user_messages\(\)', '.user_messages', content)
    content = re.sub(r'\.summaries\(\)', '.summaries', content)
    
    # Save if changed
    if content != original:
        test_file.write_text(content)
        print(f"Fixed {test_file}")

print("Done fixing test method calls")
