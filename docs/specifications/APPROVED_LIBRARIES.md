# APPROVED LIBRARIES - NO EXCEPTIONS

## ⚠️ STRICT POLICY
**NO library can be used without being on this list.**
**NO library can be added without explicit approval.**
**Violations BLOCK commits and CI/CD.**

## ✅ APPROVED Python Libraries

### Core (Required)
- `orjson` - JSON parsing (10x faster than stdlib)
- `pydantic` (v2) - Data validation and models
- `pendulum` - Date/time handling
- `loguru` - Logging
- `httpx` - HTTP client
- `watchfiles` - File watching (Rust-based)

### Data Processing (Approved)
- `toolz` - Functional programming utilities
- `more-itertools` - Advanced iteration patterns
- `networkx` - Graph operations (for thread navigation)
- `lazy-object-proxy` - Lazy loading and proxy objects (approved for streaming large files)

### CLI/Config (Approved)
- `typer` - CLI framework
- `rich` - Terminal formatting
- `pydantic-settings` - Configuration management

### Testing (Approved)
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `pytest-asyncio` - Async test support (if needed)

### Development (Approved)
- `ruff` - Linting
- `mypy` - Type checking
- `mkdocs` - Documentation
- `mkdocs-material` - Docs theme
- `pre-commit` - Git hooks

### Research/Utilities (Approved)
- `tenacity` - Retry logic
- `python-dotenv` - Environment variables

## ❌ EXPLICITLY FORBIDDEN

### Never Use These
- `asyncio` - NO manual async, use high-level libraries
- `threading` - NO manual threading
- `multiprocessing` - NO manual multiprocessing  
- `concurrent.futures` - NO manual concurrency
- `json` - Use orjson
- `datetime` - Use pendulum
- `requests` - Use httpx
- `urllib` - Use httpx
- `logging` - Use loguru
- `argparse` - Use typer
- `configparser` - Use pydantic-settings
- `tqdm` - Use rich.progress

### Low-Level (Forbidden)
- `struct` - Too low-level
- `ctypes` - Too low-level
- `socket` - Use httpx
- `pickle` - Security risk
- `eval/exec` - Security risk

## 📋 APPROVAL PROCESS

To add a new library:

1. **Research Required**: Run `python scripts/research.py "library for X"`
2. **Justification**: Explain why existing approved libraries don't work
3. **High-Level Only**: Must be a high-level library that handles complexity
4. **Get Approval**: Must be explicitly approved before adding
5. **Update This File**: Add to approved list with reason

## 🔒 ENFORCEMENT

This list is enforced by:
- `scripts/verify_spec.py` - Checks all imports
- `.git/hooks/pre-commit` - Blocks local commits
- `.github/workflows/quality-gates.yml` - Blocks PRs
- `make verify-spec` - Manual check

## 📝 NOTES

- If you need async, find a high-level library that handles it internally
- If you need threading, find a high-level library that handles it internally
- If you need concurrency, find a high-level library that handles it internally
- We use HIGH-LEVEL libraries that hide complexity, not low-level primitives