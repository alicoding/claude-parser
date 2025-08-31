# Claude Parser Development Guidelines

## Quick Start

```bash
# Verify tests pass
pytest tests/ -x

# Check code quality
python scripts/verify_spec.py
```

## Architecture Principles

- **SOLID/DRY/DDD**: Follow Domain-Driven Design
- **95/5 Rule**: 95% library code, 5% glue
- **TDD**: Write tests first
- **Small Files**: Max 150 lines per file

## Key Libraries

- **JSON**: orjson (not json)
- **Dates**: pendulum (not datetime)
- **HTTP**: httpx (not requests)
- **Logging**: loguru (not logging)
- **CLI**: typer/click (not argparse)
- **Validation**: pydantic
- **Async**: watchfiles for file watching

## Development Workflow

1. Run tests before making changes
2. Use existing patterns and conventions
3. Keep changes focused and tested
4. Verify all tests pass before committing

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_parser --cov-report=term-missing

# Run specific test
pytest tests/test_parser.py::test_specific_function
```

## Code Quality Gates

- Tests: 100% pass rate required
- Coverage: 90%+ required
- Linting: Zero violations
- Pre-commit: All hooks must pass

## Pre-commit Setup

```bash
pre-commit install
pre-commit run --all-files
```
