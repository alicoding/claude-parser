# 95/5 Principle Violations Analysis - Claude Parser Codebase

This document captures every violation found where custom code could be replaced by a library.

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/base.py
LINES ANALYZED: 61
VIOLATIONS FOUND: 0

No significant violations found. The file properly uses pydantic for data validation, pendulum for timestamp parsing, and follows good practices with type hints and enums.

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/domain/entities/conversation.py
LINES ANALYZED: 150
VIOLATIONS FOUND: 3

### VIOLATION 1:
- Lines: 121-124
- Current code: `summary_indices = [i for i, msg in enumerate(self._messages) if isinstance(msg, Summary)]`
- Issue: Manual list comprehension for finding indices
- Should use: toolz.pluck or more-itertools.locate
- Example fix: `summary_indices = list(locate(self._messages, lambda msg: isinstance(msg, Summary)))`
- LOC saved: 1-2 lines (and more functional approach)

### VIOLATION 2:
- Lines: 104-107
- Current code: Manual case-insensitive string matching in search
- Issue: Custom string lowercasing and matching logic
- Should use: re module with case-insensitive flag or use a proper text search library
- Example fix: `import re; return self.filter_messages(lambda m: re.search(re.escape(query), m.text_content, re.IGNORECASE))`
- LOC saved: 2-3 lines (and handles edge cases better)

### VIOLATION 3:
- Lines: 127-128, 132-133
- Current code: Manual slice calculations `[-limit:]`, `[start_idx:last_summary_idx]`
- Issue: Manual list slicing logic that could use itertools.islice or toolz equivalents
- Should use: more-itertools.tail() and more-itertools.take()
- Example fix: `from more_itertools import tail, take; return list(tail(limit, self._messages))`
- LOC saved: 2-3 lines (and clearer intent)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/parser.py
LINES ANALYZED: 115
VIOLATIONS FOUND: 2

### VIOLATION 1:
- Lines: 102-107
- Current code: Manual pipeline for filtering and mapping fields to copy
- Issue: Complex custom pipeline that could be simplified with toolz operations
- Should use: toolz.keyfilter or toolz.valfilter for cleaner field extraction
- Example fix: `fields_to_copy = toolz.keyfilter(lambda k: nested_msg.get(k) is not None, {f: nested_msg.get(f) for f in ['role', 'id', 'model', 'usage']})`
- LOC saved: 3-4 lines (and clearer logic)

### VIOLATION 2:
- Lines: 74-88
- Current code: Custom extract_text function with manual if/elif chains
- Issue: Could use pattern matching or a dispatch table
- Should use: singledispatch decorator or a simple dispatch dictionary
- Example fix: `BLOCK_EXTRACTORS = {'text': lambda b: b.get('text', ''), 'tool_result': lambda b: f"[Tool Result] {b.get('content', '')}", ...}`
- LOC saved: 8-10 lines (and more extensible)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/application/conversation_service.py
LINES ANALYZED: 184
VIOLATIONS FOUND: 1

### VIOLATION 1:
- Lines: 108-111
- Current code: Manual string concatenation for error messages
- Issue: Custom string building logic
- Should use: String formatting with f-strings or str.join()
- Example fix: `error_msg = f"File {filepath} is not in valid Claude Code format{': ' + '; '.join(errors) if errors else ''}"`
- LOC saved: 2-3 lines (and more readable)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/infrastructure/file_utils.py
LINES ANALYZED: 64
VIOLATIONS FOUND: 2

### VIOLATION 1:
- Lines: 35-37
- Current code: Manual list() + enumerate() for line numbering
- Issue: Loading entire file into memory unnecessarily
- Should use: itertools.enumerate directly on file iterator
- Example fix: `yield from enumerate(f, 1)` (remove the intermediate list())
- LOC saved: 2 lines (and better memory usage for large files)

### VIOLATION 2:
- Lines: 49-53
- Current code: Manual if/else for conditional logging
- Issue: Duplicated logging logic with slight variations
- Should use: String formatting with conditional expression
- Example fix: `logger.warning(f"{'Line ' + str(line_num) + ': ' if line_num else ''}Failed to parse JSON - {e}")`
- LOC saved: 3-4 lines (and DRY principle)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/infrastructure/jsonl_parser.py
LINES ANALYZED: 243
VIOLATIONS FOUND: 2

### VIOLATION 1:
- Lines: 175-179
- Current code: Manual list slicing with `[:20]` in pipeline
- Issue: Custom slicing logic within functional pipeline
- Should use: itertools.islice or more-itertools.take
- Example fix: `lambda msgs: list(take(20, msgs))`
- LOC saved: 1 line (and clearer intent)

### VIOLATION 2:
- Lines: 217-222
- Current code: Manual set filtering with None filter
- Issue: Filtering None values manually in toolz.filter
- Should use: more-itertools.compact or toolz.remove with None check
- Example fix: `session_ids = set(compact(msg.get("sessionId") for msg in messages))`
- LOC saved: 3-4 lines (and clearer logic)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/user.py
LINES ANALYZED: 30
VIOLATIONS FOUND: 0

No significant violations found. Simple pydantic model with good practices.

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/assistant.py
LINES ANALYZED: 39
VIOLATIONS FOUND: 1

### VIOLATION 1:
- Lines: 34-39
- Current code: Manual sum of optional values with `or 0` fallback
- Issue: Manual null-coalescing and addition
- Should use: operator.add with functools.reduce or sum() with generator
- Example fix: `return sum(filter(None, [self.input_tokens, self.output_tokens, self.cache_read_tokens, self.cache_write_tokens]))`
- LOC saved: 3-4 lines (and handles None values more elegantly)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/tool.py
LINES ANALYZED: 67
VIOLATIONS FOUND: 1

### VIOLATION 1:
- Lines: 55-62
- Current code: Manual if/elif/else chain for text content generation
- Issue: Complex conditional logic that could use pattern matching or dispatch
- Should use: Dictionary dispatch or match statement (Python 3.10+)
- Example fix: `TEXT_GENERATORS = {lambda: self.tool_error is not None: lambda: f"Tool Error: {self.tool_error}", ...}`
- LOC saved: 5-6 lines (and more extensible)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/domain/services/analyzer.py
LINES ANALYZED: 31
VIOLATIONS FOUND: 0

No significant violations found. Simple domain service with good separation of concerns.

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/discovery/transcript_finder.py
LINES ANALYZED: 266
VIOLATIONS FOUND: 2

### VIOLATION 1:
- Lines: 117-118
- Current code: Manual list sorting with lambda key function
- Issue: Manual sorting implementation  
- Should use: operator.itemgetter for cleaner sorting
- Example fix: `from operator import itemgetter; transcripts.sort(key=itemgetter('modified'), reverse=True)`
- LOC saved: 1 line (and clearer intent)

### VIOLATION 2:
- Lines: 227-231
- Current code: Complex filtering with orjson.loads inside filter
- Issue: Manual parsing and filtering logic that could fail
- Should use: itertools.dropwhile or more-itertools.first with exception handling
- Example fix: Use first() with a more robust parsing function
- LOC saved: 2-3 lines (and better error handling)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/infrastructure/message_repository.py
LINES ANALYZED: 200
VIOLATIONS FOUND: 3

### VIOLATION 1:
- Lines: 100-101
- Current code: `lines = list(f)` - Loading entire file into memory
- Issue: Manual file loading that could use more efficient approaches
- Should use: itertools.islice or more-itertools for lazy loading
- Example fix: Process lines lazily without loading all into memory first
- LOC saved: 1 line (and better memory usage)

### VIOLATION 2:
- Lines: 163
- Current code: `lambda ids: next(iter(ids), None)`
- Issue: Manual next/iter pattern for getting first element
- Should use: more-itertools.first()
- Example fix: `lambda ids: first(ids, default=None)`
- LOC saved: 1 line (and clearer intent)

### VIOLATION 3:
- Lines: 172
- Current code: Repeated pattern of `next(iter(values), None)` in extract_field
- Issue: Duplicated pattern extraction logic  
- Should use: more-itertools.first() consistently
- Example fix: Use first() everywhere instead of manual next/iter
- LOC saved: 2-3 lines (and DRY principle)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/features/registry.py
LINES ANALYZED: 86
VIOLATIONS FOUND: 1

### VIOLATION 1:
- Lines: 46-51
- Current code: Manual list of status enums and filter check
- Issue: Hardcoded list that should be derived from enum
- Should use: enum methods or set operations
- Example fix: `incomplete = set(FeatureStatus) - {FeatureStatus.COMPLETE, FeatureStatus.DEPRECATED}`
- LOC saved: 2-3 lines (and more maintainable)

---

# ANALYSIS SUMMARY

## Total Files Analyzed: 12
- claude_parser/__init__.py
- claude_parser/models/base.py  
- claude_parser/domain/entities/conversation.py
- claude_parser/models/parser.py
- claude_parser/application/conversation_service.py
- claude_parser/infrastructure/file_utils.py
- claude_parser/infrastructure/jsonl_parser.py
- claude_parser/models/user.py
- claude_parser/models/assistant.py
- claude_parser/models/tool.py
- claude_parser/domain/services/analyzer.py
- claude_parser/discovery/transcript_finder.py
- claude_parser/infrastructure/message_repository.py
- claude_parser/features/registry.py

## Total Violations Found: 18

## Most Common Violation Types:
1. **Manual iterations/loops**: 6 violations - Should use more-itertools, toolz
2. **String manipulation**: 3 violations - Should use string formatting libraries
3. **Pattern matching/conditionals**: 3 violations - Should use dispatch tables, match statements
4. **Collection operations**: 3 violations - Should use functional library methods
5. **Manual parsing/filtering**: 3 violations - Should use specialized parsing libraries

## Libraries That Could Eliminate Most Violations:
1. **more-itertools** - Would fix 8+ violations (first(), take(), tail(), locate(), compact())
2. **operator module** - Would fix 3 violations (itemgetter, methodcaller)
3. **functools.singledispatch** - Would fix 2 violations (dispatch tables)
4. **itertools** - Would fix 2+ violations (islice instead of manual slicing)
5. **Pattern matching (Python 3.10+)** - Would fix 2 violations

## Estimated Total LOC That Could Be Eliminated: 35-50 lines
## Estimated Maintenance Reduction: 20-30% (cleaner, more intention-revealing code)

The codebase is generally well-structured with good use of libraries like toolz, orjson, and pydantic. However, there are still opportunities to further reduce custom code by leveraging specialized libraries for common patterns.

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/__init__.py
LINES ANALYZED: 118
VIOLATIONS FOUND: 1

### VIOLATION 1:
- Lines: 82
- Current code: `total_messages = reduce(lambda acc, c: acc + len(c), convs, 0)`
- Issue: Using reduce from functools for simple sum operation
- Should use: Built-in sum() function or toolz.reduce_by
- Example fix: `total_messages = sum(len(c) for c in convs)`
- LOC saved: 0 (but cleaner and more readable)

---

## FILE: /Users/ali/.claude/projects/claude-parser/claude_parser/models/base.py
LINES ANALYZED: 61
VIOLATIONS FOUND: 0

No significant violations found. The file properly uses pydantic for data validation, pendulum for timestamp parsing, and follows good practices with type hints and enums.

---
