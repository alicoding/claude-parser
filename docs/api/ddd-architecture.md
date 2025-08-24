# DDD Architecture Documentation

## Overview

Claude Parser follows Domain-Driven Design (DDD) principles with clean separation of concerns across three layers:

1. **Domain Layer** - Core business logic and entities
2. **Infrastructure Layer** - Data access and external concerns
3. **Application Layer** - Use cases and orchestration

## Architecture Layers

### Domain Layer (`claude_parser/domain/`)

The heart of the application containing pure business logic:

- **Conversation** - Aggregate root representing a Claude conversation
- **ConversationMetadata** - Value object for conversation metadata
- **ConversationAnalyzer** - Domain service for analysis operations
- **Message Filters** - Strategy pattern implementations for filtering

```python
# Example: Domain entity with rich behavior
conversation = Conversation(messages, metadata)
assistant_msgs = conversation.assistant_messages  # Property
results = conversation.search("error")  # Domain operation
```

### Infrastructure Layer (`claude_parser/infrastructure/`)

Handles all external concerns and data access:

- **JsonlMessageRepository** - Repository pattern for JSONL file access
- Uses `orjson` for fast JSON parsing (10x faster than standard json)
- Uses `pydantic` for validation and type safety

```python
# Example: Repository handles data access
repository = JsonlMessageRepository()
messages = repository.load_messages(filepath)
metadata = repository.get_metadata(messages, filepath)
```

### Application Layer (`claude_parser/application/`)

Orchestrates between domain and infrastructure:

- **ConversationService** - Application service coordinating operations
- Implements the main factory methods like `load_conversation()`
- Follows 95/5 principle - simple for common cases

```python
# Example: Application service orchestration
service = ConversationService()
conversation = service.load_conversation("session.jsonl")
```

## Key Patterns Used

### Repository Pattern
- Abstracts data access behind interfaces
- Domain doesn't know about file systems or JSON
- Easy to swap data sources (files, databases, APIs)

### Factory Pattern
- Simple `load()` function for 95% use cases
- Complex operations available through services
- Zero configuration required

### Strategy Pattern
- Message filters as strategies
- Pluggable filtering logic
- Easy to extend with new filter types

### Value Objects
- Immutable message models
- ConversationMetadata as value object
- Type safety through Pydantic

## SOLID Principles

### Single Responsibility (SRP)
- Each class has one reason to change
- Conversation handles conversation logic only
- Repository handles data access only

### Open/Closed (OCP)
- Open for extension via composition
- Closed for modification
- New features through new classes, not modifying existing

### Liskov Substitution (LSP)
- All messages implement common interface
- Can substitute message types transparently
- Polymorphic message handling

### Interface Segregation (ISP)
- Focused interfaces, no god objects
- MessageFilter protocol for filters
- MessageRepository abstract base

### Dependency Inversion (DIP)
- Domain depends on abstractions
- Infrastructure implements domain interfaces
- Application orchestrates without tight coupling

## 95/5 Principle

The API follows the 95/5 principle:

**95% Use Case - Dead Simple**
```python
from claude_parser import load

conv = load("session.jsonl")
print(len(conv.messages))
print(conv.assistant_messages[0].text_content)
```

**5% Use Case - Full Power**
```python
from claude_parser.application import ConversationService
from claude_parser.infrastructure import JsonlMessageRepository

# Custom repository with special handling
repo = JsonlMessageRepository()
service = ConversationService(repo)
conv = service.load_conversation("session.jsonl")

# Advanced domain operations
analyzer = ConversationAnalyzer(conv)
stats = analyzer.get_stats()
```

## Benefits of DDD Architecture

1. **Testability** - Each layer can be tested independently
2. **Maintainability** - Clear boundaries and responsibilities
3. **Extensibility** - Easy to add new features without breaking existing
4. **Performance** - Optimized data access with orjson and pydantic
5. **Type Safety** - Full type hints and validation throughout

## Migration from Simple Architecture

The codebase was migrated from a simple single-file implementation to full DDD:

**Before**: Single `conversation.py` with all logic mixed
**After**: Clean separation across domain, infrastructure, and application layers

This migration ensures:
- Better long-term maintainability
- Easier to add new features
- Cleaner test structure
- Professional enterprise-grade architecture

## File Structure

```
claude_parser/
├── __init__.py           # Main API exports
├── domain/
│   ├── __init__.py
│   └── conversation.py   # Domain entities and logic
├── infrastructure/
│   ├── __init__.py
│   └── message_repository.py  # Data access
├── application/
│   ├── __init__.py
│   └── conversation_service.py  # Use cases
└── models.py            # Shared message models
```

## Usage Examples

### Basic Usage
```python
from claude_parser import load

# Load conversation
conv = load("chat.jsonl")

# Access messages
print(f"Total: {len(conv.messages)}")
print(f"Assistant: {len(conv.assistant_messages)}")
print(f"User: {len(conv.user_messages)}")

# Search
errors = conv.search("error")
```

### Advanced Usage
```python
from claude_parser.domain import ConversationAnalyzer

# Analysis
analyzer = ConversationAnalyzer(conv)
stats = analyzer.get_stats()

# Custom filtering
from claude_parser.domain.conversation import ContentFilter

filter = ContentFilter("python", case_sensitive=False)
python_msgs = [m for m in conv.messages if filter.matches(m)]
```

## Testing Strategy

Tests are organized by layer:

- `tests/test_domain_*.py` - Domain logic tests
- `tests/test_infrastructure_*.py` - Repository tests
- `tests/test_application_*.py` - Service tests
- `tests/test_integration.py` - Full stack tests

## Performance Considerations

- **orjson** for JSON parsing - 10x faster than standard json
- **pydantic v2** for validation - Optimized with Rust
- **Lazy loading** - Messages parsed on demand
- **Index building** - O(1) UUID lookups via hashmaps

## Future Enhancements

Possible extensions while maintaining DDD:

1. **Event Sourcing** - Track conversation changes as events
2. **CQRS** - Separate read and write models
3. **Async Support** - Async repository implementations
4. **Caching Layer** - Add caching repository decorator
5. **Multiple Formats** - Support CSV, Parquet, etc.

The DDD architecture makes these enhancements straightforward without major refactoring.