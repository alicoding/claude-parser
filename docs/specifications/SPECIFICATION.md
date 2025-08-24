# Claude Parser SDK - BDD Specification & Implementation Contract

## CRITICAL: Implementation Rules (MUST READ FIRST)

### 95/5 Library Choices (NO EXCEPTIONS - Updated 2025-08-20)
```yaml
# Based on real-time research using sonar-pro model
HTTP Requests: httpx       # NEVER use requests, urllib (3-10x faster, async)
JSON Parsing: orjson       # NEVER use json, ujson (10x faster, Rust-based)
Validation: pydantic v2    # NEVER write custom validators (10x faster than v1)
CLI: typer                 # NEVER use click, argparse (type hints based)
Testing: pytest            # NEVER use unittest (best fixtures)
File Watching: watchfiles  # NEVER use watchdog (10x faster, Rust-based)
Task Queue: dramatiq       # NEVER use celery (50% less config)
Events: blinker           # NEVER use pluggy (simpler, Flask-tested)
Async: NONE (sync first)  # NEVER use asyncio (if async needed: anyio)
Dates: pendulum           # NEVER use datetime directly
Config: pydantic-settings # NEVER use configparser
Logging: loguru           # NEVER use logging module
Progress: rich            # NEVER use tqdm
TypeScript HTTP: ky       # NEVER use fetch, axios (smallest, cleanest)
TypeScript Validation: zod # NEVER use joi, yup (best TS integration)
TypeScript Testing: vitest # NEVER use jest (3x faster)
```

### Anti-Patterns That FAIL Review
1. **Writing custom JSON parser** → Use orjson
2. **Manual type checking** → Use pydantic/zod
3. **String concatenation for paths** → Use pathlib/path.join
4. **try/except without specific errors** → Always catch specific
5. **Global state** → Use dependency injection
6. **Hardcoded values** → Use constants/enums
7. **Sync file operations in async** → Use aiofiles
8. **Manual retry logic** → Use tenacity/p-retry

## Feature Specifications (BDD Format)

### Feature: JSONL Parser
```gherkin
Feature: Parse Claude Code JSONL files
  As a developer
  I want to parse Claude's conversation files
  So that I can analyze and process conversations

  Background:
    Given the parser uses orjson for JSON parsing
    And the parser uses pydantic for validation
    And the parser NEVER uses json.loads directly

  Scenario: Parse valid JSONL file
    Given a valid Claude JSONL file "conversation.jsonl"
    When I call ClaudeParser.load("conversation.jsonl")
    Then I receive a Conversation object
    And all messages are validated with pydantic
    And the parsing takes < 100ms per MB

  Scenario: Handle malformed lines
    Given a JSONL file with malformed line 5
    When I parse in recovery mode
    Then line 5 is logged with loguru
    And valid lines are still parsed
    And I can access parser.errors list

  Verification Criteria:
    ✓ Uses orjson.loads, not json.loads
    ✓ All models inherit from pydantic.BaseModel
    ✓ Performance: 10MB file < 1 second
    ✓ Memory: Streaming mode for files > 100MB
    ✓ Test coverage > 95%
```

### Feature: Message Extraction
```gherkin
Feature: Extract specific message types
  As a developer
  I want to query messages by type
  So that I can analyze specific interactions

  Background:
    Given messages are pydantic models
    And queries use generator expressions for memory efficiency
    And NEVER load entire file for single queries

  Scenario: Get assistant messages
    Given a conversation with 1000 messages
    When I access conv.assistant_messages
    Then I receive only type="assistant" messages
    And it returns a lazy iterator, not a list
    And memory usage stays constant

  Scenario: Get messages before summary
    Given a conversation with summary at line 500
    When I call conv.before_summary(20)
    Then I receive messages 480-499
    And the operation uses backward iteration
    And doesn't load messages 1-479

  Verification Criteria:
    ✓ All queries return iterators by default
    ✓ .to_list() explicitly creates lists
    ✓ Uses @cached_property for repeated access
    ✓ Memory profile shows no leaks
```

### Feature: Event Monitoring
```gherkin
Feature: Real-time JSONL monitoring
  As a developer
  I want to monitor JSONL files for changes
  So that I can react to new messages

  Background:
    Given monitoring uses watchfiles library
    And events use asyncio, not threading
    And NEVER polls the file manually

  Scenario: Monitor for new messages
    Given an active JSONL file
    When I start monitoring with watcher.start()
    Then new lines trigger message events
    And events are debounced (100ms)
    And file locks are respected

  Scenario: Handle concurrent writes
    Given multiple processes writing to JSONL
    When monitoring the file
    Then partial writes are buffered
    And only complete JSON lines are parsed
    And no data corruption occurs

  Verification Criteria:
    ✓ Uses watchfiles, not custom file watching
    ✓ Async event handlers with asyncio
    ✓ Debouncing with asyncio.wait_for
    ✓ File locking with portalocker
```

### Feature: Memory Integration
```gherkin
Feature: Export to memory systems
  As a developer
  I want to export conversations to mem0
  So that I can build memory-augmented applications

  Background:
    Given mem0 integration uses official SDK
    And vector embeddings use sentence-transformers
    And NEVER implement custom embedding logic

  Scenario: Export to mem0
    Given a conversation with 100 messages
    When I call conv.to_mem0()
    Then messages are chunked by context
    And metadata includes session, timestamp, type
    And mem0.add_memories is called in batches

  Scenario: Generate embeddings
    Given messages needing vectorization
    When I call conv.to_embeddings()
    Then sentence-transformers creates vectors
    And embeddings are cached with diskcache
    And batch size respects model limits

  Verification Criteria:
    ✓ Uses mem0 official SDK
    ✓ Uses sentence-transformers for embeddings
    ✓ Caching with diskcache library
    ✓ Batch operations for efficiency
```

### Feature: Analytics
```gherkin
Feature: Conversation analytics
  As a developer
  I want to analyze conversation patterns
  So that I can understand Claude usage

  Background:
    Given analytics use pandas for aggregation
    And visualizations use plotly
    And NEVER write custom statistical functions

  Scenario: Calculate token usage
    Given a conversation with messages
    When I call conv.analytics.token_count
    Then tiktoken counts tokens accurately
    And results are cached per message
    And totals are aggregated with pandas

  Scenario: Identify error patterns
    Given conversations with errors
    When I call analytics.error_patterns()
    Then common errors are grouped
    And frequency is calculated with pandas
    And results include suggestions

  Verification Criteria:
    ✓ Uses tiktoken for token counting
    ✓ Uses pandas for all aggregations
    ✓ Visualizations with plotly only
    ✓ Statistics with scipy.stats
```

## Implementation Checklist for Each Feature

### Before Starting ANY Feature:
- [ ] Read SPECIFICATION.md library choices
- [ ] Check if library is already in pyproject.toml
- [ ] If HTTP needed: use ky
- [ ] If JSON needed: use orjson  
- [ ] If validation needed: use pydantic
- [ ] If dates needed: use pendulum

### Definition of Done:
- [ ] Uses specified libraries (no alternatives)
- [ ] All models are pydantic.BaseModel
- [ ] Async operations use asyncio
- [ ] Logging uses loguru
- [ ] Tests use pytest
- [ ] Type hints on all functions
- [ ] Docstrings follow Google style
- [ ] No TODO comments
- [ ] Performance criteria met
- [ ] Memory criteria met

## Verification Scripts

### Script to Check Compliance
```python
# Run this to verify implementation follows spec
def verify_no_forbidden_imports():
    forbidden = [
        "import json",  # Must use orjson
        "import requests",  # Must use ky
        "import urllib",  # Must use ky
        "from datetime import",  # Must use pendulum
        "import threading",  # Must use asyncio
        "import logging",  # Must use loguru
    ]
    # Check all .py files for forbidden imports
    
def verify_95_5_principle():
    # Check that simple API is actually simple
    # conv = load("file.jsonl")  # Should work
    # conv.messages  # Should work
    # No configuration needed for basic use
```

## Session Handoff Rules

### When Starting New Session:
1. Run: `python verify_spec.py` to check compliance
2. Read library choices section
3. Pick next feature from backlog
4. Implement ONLY with specified libraries
5. If tempted to write custom code, CHECK SPEC FIRST

### Red Flags That Need Correction:
- "Let me implement a custom..."
- "I'll write a simple function to..."
- "We don't need a library for..."
- "Fetch is simpler than ky..."
- Using json.loads instead of orjson.loads

## Examples of 95/5 in Practice

### 95% Use Case (Simple)
```python
from claude_parser import load

# This MUST work with zero configuration
conv = load("chat.jsonl")
print(conv.messages)
print(conv.assistant_messages)
```

### 5% Use Case (Advanced)
```python
from claude_parser import Parser

# Advanced users can configure
parser = Parser()
    .with_recovery_mode()
    .with_validation(strict=False)
    .with_streaming(chunk_size=1000)
    
conv = await parser.parse_async("huge.jsonl")
```

## The 95/5 Test
If a new developer can't use your feature in 1 line of code for the common case, you've failed the 95/5 principle.

## Library Documentation Links
- ky: https://github.com/sindresorhus/ky
- orjson: https://github.com/ijl/orjson
- pydantic: https://docs.pydantic.dev
- loguru: https://github.com/Delgan/loguru
- pendulum: https://pendulum.eustace.io
- click: https://click.palletsprojects.com
- rich: https://rich.readthedocs.io
- tenacity: https://tenacity.readthedocs.io
- watchfiles: https://watchfiles.helpmanual.io
- mem0: https://docs.mem0.ai
- tiktoken: https://github.com/openai/tiktoken
- sentence-transformers: https://sbert.net