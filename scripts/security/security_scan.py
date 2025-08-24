#!/usr/bin/env python3
"""
Security scan for GitHub preparation.
Checks for secrets, API keys, and sensitive data.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Patterns to detect secrets
SECRET_PATTERNS = [
    (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'API Key'),
    (r'helix-[\w-]{40,}', 'Helix API Key'),
    (r'sk-[\w]{48}', 'OpenAI Key'),
    (r'ghp_[\w]{36}', 'GitHub Token'),
    (r'aws[_-]?secret[_-]?access[_-]?key', 'AWS Secret'),
    (r'BEGIN PRIVATE KEY', 'Private Key'),
    (r'/Users/ali/', 'Absolute Path'),
    (r'ali@alicoding\.com', 'Email Address'),
]

def scan_file(file_path: Path) -> List[Tuple[str, int, str]]:
    """Scan a single file for secrets."""
    issues = []
    try:
        content = file_path.read_text()
        for line_no, line in enumerate(content.splitlines(), 1):
            for pattern, secret_type in SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append((str(file_path), line_no, secret_type))
    except:
        pass
    return issues

def main():
    """Run security scan."""
    print("🔍 Security Scan for GitHub\n")
    
    # Files to scan
    py_files = list(Path('.').rglob('*.py'))
    config_files = ['.env', '.env.example', 'pyproject.toml']
    
    all_issues = []
    
    # Scan Python files
    for file_path in py_files:
        # Skip test files and examples
        if 'test' in str(file_path) or 'example' in str(file_path):
            continue
        issues = scan_file(file_path)
        all_issues.extend(issues)
    
    # Check for .env file
    if Path('.env').exists():
        print("⚠️  .env file exists - ensure it's in .gitignore")
    
    # Report findings
    if all_issues:
        print("❌ Found security issues:\n")
        for file_path, line_no, issue_type in all_issues:
            print(f"  {file_path}:{line_no} - {issue_type}")
        print(f"\n❌ Total issues: {len(all_issues)}")
        return 1
    else:
        print("✅ No secrets found!")
        print("✅ Ready for GitHub!")
        return 0

if __name__ == "__main__":
    exit(main())