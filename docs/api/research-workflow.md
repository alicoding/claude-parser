# Research Workflow

## Mandatory Research Process

Before implementing ANY new feature, you MUST research existing 95/5 solutions using our research tool.

## Quick Start

```bash
# Interactive research mode
make research

# Single query research
make research-query QUERY="async file watching python"

# Direct script usage
python scripts/research.py "your research query"
```

## Research Tool Features

- **95/5 Architecture Focus** - Finds high-level libraries that handle 95% of complexity
- **Latest Solutions** - Focuses on 2025 best practices and modern libraries
- **Code Reduction Estimates** - Shows percentage of code reduction when using recommended solutions
- **Practical Examples** - Provides migration paths and real code comparisons
- **Auto-Documentation** - Saves all research to `docs/research/` with timestamps

## Example Usage

### Before Adding Async Support
```bash
python scripts/research.py "async file watching python 2025 high-level library"
```

### Before Adding Database Support
```bash
python scripts/research.py "python ORM database library 95/5 principle SQLAlchemy alternative"
```

### Before Adding HTTP Client
```bash
python scripts/research.py "python http client library httpx vs requests 2025"
```

## Research Output

The tool automatically:
1. **Streams results** in real-time with rich formatting
2. **Saves to markdown** in `docs/research/research_TIMESTAMP.md`
3. **Maintains conversation history** for follow-up questions
4. **Provides structured recommendations** with:
   - Clear recommendation with justification
   - Code reduction percentage
   - Migration examples
   - Comparison tables

## Integration with Development Workflow

### 1. Research Phase (MANDATORY)
```bash
make research
```

### 2. Document Findings
Research is auto-saved to `docs/research/` - review and integrate into specs.

### 3. Update Specifications
Add approved libraries to `docs/api/SPECIFICATION.md`

### 4. Implement with 95/5 Libraries
Use only high-level libraries found during research.

## Example Research Session

```
💭 Query: async file watching python high-level library

🔍 Research Query:
async file watching python high-level library

Research Results:
Based on the 95/5 principle, here are the top high-level libraries for async file watching in Python:

## Recommended: `watchfiles`

**Code Reduction: ~85%**

### Why watchfiles?
- Built on Rust (fast and reliable)
- Async/await native support
- Cross-platform (Linux, macOS, Windows)
- Minimal configuration required
- Active maintenance (2025)

### Migration Example:
```python
# Low-level approach (complex)
import asyncio
import os
from pathlib import Path

# 85% less code with watchfiles
import asyncio
from watchfiles import awatch

async def watch_files():
    async for changes in awatch('./'):
        print(f'Changes: {changes}')
```

📁 Research saved to: docs/research/research_20250821_120000.md
```

## Best Practices

1. **Always research first** - Never implement without checking for existing solutions
2. **Ask follow-up questions** - The tool maintains conversation context
3. **Document decisions** - Research files serve as architectural decision records
4. **Update specifications** - Add approved libraries to project specs
5. **Share findings** - Research files can be shared with team members

## Research Quality Guidelines

### Good Research Queries
- "python async file watching high-level library 2025"
- "SQLAlchemy alternative lightweight ORM 95/5 principle"
- "pytest fixtures replacement modern testing library"

### Poor Research Queries
- "file watching"
- "database"
- "testing"

Be specific about:
- Language/technology
- Use case
- Architectural preference (95/5, high-level)
- Year/recency requirements

## Environment Setup

The research tool requires:
- `OPENAI_API_KEY` environment variable
- `OPENAI_BASE_URL` (optional, defaults to electronhub.ai)

Configure in `.env`:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.electronhub.ai/v1
```

This research workflow ensures we always use the best available libraries and avoid reinventing the wheel.