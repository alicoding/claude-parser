# Contributing to Claude Parser

Thank you for your interest in contributing to Claude Parser!

## Development Setup

```bash
# Install dependencies
poetry install

# Run tests
pytest

# Run linting
ruff check .

# Format code
ruff format .
```

## Code Quality Standards

- **Test Coverage**: Maintain 90%+ test coverage
- **Architecture**: Follow SOLID/DRY/DDD principles
- **File Size**: Keep files under 150 lines
- **Dependencies**: Use established libraries (95% library, 5% glue code)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_parser

# Run specific test file
pytest tests/test_parser.py
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
pre-commit install
pre-commit run --all-files
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## Code Style

- Use type hints
- Follow PEP 8
- Write descriptive docstrings
- Keep functions focused and small

## Questions?

Open an issue on GitHub for any questions or discussions.
