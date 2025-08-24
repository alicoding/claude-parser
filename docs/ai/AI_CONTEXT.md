# Claude Parser SDK - AI Context Document

## 🚨 CRITICAL: READ THIS FIRST
This document provides comprehensive codebase awareness to prevent:
- **Duplicate implementations** (hallucination)
- **Wrong file placement** (architectural violations)
- **DRY violations** (missing similar code patterns)
- **Reinventing existing functionality**

## Project Overview
- **Name**: claude-parser
- **Purpose**: Parse Claude Code JSONL files for memory systems, events, and analytics
- **Principles**: 95/5 (95% libraries, 5% glue), SOLID, DDD, TDD, DRY
- **Total Files**: 79 Python files
- **Total Lines**: 9,545 LOC
- **Total Classes**: 85
- **Total Functions**: 138

## Domain Structure & Responsibilities

### 📦 claude_parser Package (Main SDK)

#### core/ - Core functionality and main exports
- **Files**: 1
- **Purpose**: Main package exports and initialization
- **Key Components**:
  - `__init__.py`: Package initialization and public API exports

#### models/ - Data models and domain entities  
- **Files**: 8
- **Classes**: 8
- **Purpose**: Domain entities following DDD principles
- **Key Classes**:
  - `Message`: Core message entity
  - `Conversation`: Conversation aggregate
  - `Event`: Event value objects
  - `Parser`: Parser models for JSONL handling
- **IMPORTANT**: All models use Pydantic for validation

#### features/ - Feature registry and capability tracking
- **Files**: 7  
- **Classes**: 4
- **Functions**: 10
- **Purpose**: Track SDK capabilities and implementation status
- **Key Components**:
  - `FeatureRegistry`: Main registry class
  - `Feature`: Feature model with status tracking
  - `FeatureStatus`: Enum for implementation status
  - `FeatureCategory`: Enum for feature categories
- **Use Case**: Prevent duplicate feature implementation

#### hooks/ - Hook system for Claude Code integration
- **Files**: 5
- **Classes**: 2
- **Functions**: 5
- **Purpose**: Integration with Claude Code's hook system
- **Key Functions**:
  - `hook_input()`: Process hook inputs
  - `exit_success()`: Success exit handler
  - `json_output()`: Format JSON for Claude Code
  - `advanced.allow/deny/ask()`: Permission helpers

#### watch/ - File watching and monitoring
- **Files**: 2
- **Classes**: 1
- **Functions**: 3
- **Purpose**: Monitor JSONL files for changes
- **Key Components**:
  - `watch()`: Main watch function with callbacks
  - `Watcher`: File watching implementation
- **Dependencies**: Uses watchfiles library

#### discovery/ - Discovery domain functionality
- **Files**: 2
- **Functions**: 9
- **Purpose**: Discover and search JSONL files
- **Key Functions**:
  - `find_files()`: Find JSONL files in directories
  - `search_conversations()`: Search across multiple files

#### application/ - Application services
- **Files**: 2
- **Classes**: 1
- **Functions**: 5
- **Purpose**: Application-level services and use cases
- **Key Components**:
  - Service layer implementations
  - Use case orchestration

#### infrastructure/ - Infrastructure and utilities
- **Files**: 4
- **Classes**: 1
- **Functions**: 10
- **Purpose**: Technical infrastructure and shared utilities
- **Key Components**:
  - `file_utils.py`: File handling utilities (DRY compliance)
  - `ensure_file_exists()`: Shared file validation
  - `read_jsonl_file()`: JSONL reading utility
  - Path handling and validation

#### domain/ - Domain services and repositories
- **Files**: 14
- **Classes**: 9
- **Purpose**: Domain logic and data access
- **Key Components**:
  - Repositories for data access
  - Domain services for business logic
  - Value objects and specifications

### 📁 Other Directories

#### tests/ - Test suites
- **Files**: 26
- **Purpose**: Comprehensive test coverage (>90% required)
- **Categories**:
  - Unit tests for all domains
  - Integration tests with real JSONL
  - Edge case testing
  - Performance tests

#### scripts/ - CLI tools and utilities
- **Files**: 6
- **Purpose**: Development and analysis tools
- **Key Scripts**:
  - `research.py`: Perplexity research tool
  - `feature_matrix.py`: Feature tracking CLI
  - `verify_spec.py`: Specification compliance checker
  - `codebase_inventory.py`: This inventory generator
  - `fix_violations.py`: Auto-fix code violations

#### docs/ - Documentation
- **Structure**:
  - `LIBRARY_FIRST_RULE.md`: Core development principle
  - `JSONL-STRUCTURE.md`: Claude JSONL format reference
  - `SPECIFICATION.md`: Library choices (no exceptions)
  - `ai/`: AI-specific documentation (this file)

## Key Design Patterns Used

### 1. Domain-Driven Design (DDD)
- **Entities**: Message, Conversation
- **Value Objects**: Events, Timestamps
- **Aggregates**: Conversation (aggregate root)
- **Repositories**: MessageRepository, ConversationRepository
- **Services**: ConversationService, ParserService

### 2. Functional Programming (95/5)
- **toolz**: Used for all functional operations
- **No manual loops**: Everything uses map/filter/reduce
- **Immutable operations**: Prefer pure functions

### 3. Dependency Injection
- **Interfaces**: Abstract base classes for contracts
- **Implementations**: Concrete classes in infrastructure
- **No hard dependencies**: Everything injected

## Libraries Used (MANDATORY - NO ALTERNATIVES)
Per SPECIFICATION.md, these are the ONLY allowed libraries:

### Core Libraries
- **orjson**: JSON parsing (NOT json)
- **pendulum**: Date/time handling (NOT datetime)
- **pydantic**: Data validation and models
- **toolz**: Functional programming utilities
- **httpx**: HTTP client (NOT requests/urllib)

### CLI/Development
- **typer**: CLI framework (NOT argparse)
- **rich**: Terminal output formatting
- **loguru**: Logging (NOT logging module)

### Testing
- **pytest**: Testing framework (NOT unittest)
- **pytest-cov**: Coverage reporting

### Infrastructure
- **watchfiles**: File watching (NOT manual polling)
- **tenacity**: Retry logic (NOT manual try/except)
- **apscheduler**: Scheduling (NOT while True loops)

## Common Pitfalls to Avoid

### ❌ DO NOT:
1. **Create new parsers** - Use existing `claude_parser.load()`
2. **Add JSON handling** - Already in infrastructure/file_utils.py
3. **Create new models** - Check models/ directory first
4. **Add file utilities** - Use infrastructure/file_utils.py
5. **Manual loops** - Use toolz functional operations
6. **Import json/datetime** - Use orjson/pendulum
7. **Create feature tracking** - Use features/registry.py
8. **Add hook helpers** - Check hooks/ directory first

### ✅ ALWAYS:
1. **Check existing functionality** before implementing
2. **Use domain structure** for proper file placement
3. **Follow 95/5 principle** - maximize library usage
4. **Maintain <150 LOC** per file (enforced)
5. **Write tests first** (TDD required)
6. **Use functional approach** with toolz
7. **Check feature registry** before adding features

## File Placement Guide

### Where to add new code:
- **New models/entities** → `models/[entity].py`
- **New features** → Update `features/feature_data.py`
- **File operations** → `infrastructure/file_utils.py`
- **Hook integrations** → `hooks/`
- **Domain logic** → `domain/services/`
- **Data access** → `domain/repositories/`
- **CLI commands** → `scripts/`
- **Tests** → `tests/test_[feature].py`

## Quick Reference: Most Used Functions

### Loading JSONL
```python
from claude_parser import load
conversation = load("file.jsonl")
```

### Feature Registry
```python
from claude_parser.features import get_registry
registry = get_registry()
incomplete = registry.get_incomplete_features()
```

### Hook Helpers
```python
from claude_parser.hooks import advanced
advanced.allow("Approved")
advanced.deny("Security violation")
advanced.ask("Need user confirmation")
```

### File Utilities
```python
from claude_parser.infrastructure.file_utils import ensure_file_exists
path = ensure_file_exists(filepath)
```

## Testing Requirements
- **Minimum coverage**: 90% (enforced)
- **New code**: 100% coverage required
- **Real data tests**: Use actual Claude JSONL files
- **Edge cases**: Required for all features

## Enforcement
- **Pre-commit hooks**: Block violations automatically
- **CI/CD**: GitHub Actions enforce all rules
- **No bypass**: Must fix violations to proceed

---

**IMPORTANT**: This document is auto-generated. Run `python scripts/codebase_inventory.py` to update.