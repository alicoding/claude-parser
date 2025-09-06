#!/usr/bin/env python3
"""
Sanitize JSONL files by removing secrets and sensitive data.
"""
import orjson
import re
from pathlib import Path

def sanitize_line(line: str) -> str:
    """Remove secrets from a single JSONL line."""
    try:
        data = orjson.loads(line)

        # Convert to string for regex replacement
        json_str = orjson.dumps(data).decode('utf-8')

        # List of patterns to replace
        patterns = [
            # API Keys
            (r'sk-proj-[A-Za-z0-9_\-]{40,}', 'REDACTED_OPENAI_KEY'),
            (r'ek-proxy-[A-Za-z0-9]{40,}', 'REDACTED_ELECTRONHUB_KEY'),
            (r'"api[_-]?key"\s*:\s*"[^"]{20,}"', '"api_key": "REDACTED"'),
            (r'"token"\s*:\s*"[^"]{20,}"', '"token": "REDACTED"'),
            (r'Bearer [A-Za-z0-9_\-\.]{20,}', 'Bearer REDACTED'),

            # URLs with potential credentials
            (r'https?://[^"\s]*@[^"\s]+', 'https://REDACTED_URL'),

            # AWS/Cloud credentials
            (r'AKIA[A-Z0-9]{16}', 'REDACTED_AWS_KEY'),
            (r'aws_secret_access_key["\s]*[=:]["\s]*[A-Za-z0-9/+=]{40}', 'aws_secret_access_key=REDACTED'),

            # Database URLs
            (r'(mongodb|postgresql|mysql|redis)://[^"\s]+', r'\1://REDACTED_CONNECTION'),

            # SSH Keys
            (r'-----BEGIN [A-Z ]+-----[\s\S]*?-----END [A-Z ]+-----', 'REDACTED_PRIVATE_KEY'),
            (r'ssh-rsa [A-Za-z0-9+/=]{100,}', 'ssh-rsa REDACTED'),
        ]

        # Apply all patterns
        for pattern, replacement in patterns:
            json_str = re.sub(pattern, replacement, json_str, flags=re.IGNORECASE)

        # Parse back to ensure valid JSON
        sanitized = orjson.loads(json_str)

        return orjson.dumps(sanitized).decode('utf-8')
    except orjson.JSONDecodeError:
        # If not valid JSON, return empty line
        return ""
    except Exception as e:
        print(f"Error sanitizing line: {e}")
        return ""

def sanitize_jsonl_file(input_path: Path, output_path: Path):
    """Sanitize an entire JSONL file."""
    print(f"Sanitizing {input_path.name}...")

    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            sanitized = sanitize_line(line)
            if sanitized:
                outfile.write(sanitized + '\n')

            if line_num % 1000 == 0:
                print(f"  Processed {line_num} lines...")

    print(f"  ✅ Saved to {output_path.name}")

def main():
    # Source directory with original files
    source_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser")

    # Output directory for sanitized files
    output_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/test-data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each JSONL file
    for jsonl_file in source_dir.glob("*.jsonl"):
        output_file = output_dir / jsonl_file.name
        sanitize_jsonl_file(jsonl_file, output_file)

    print("\n✅ All files sanitized successfully!")

if __name__ == "__main__":
    main()
