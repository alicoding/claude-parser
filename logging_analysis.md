# Complete Logging Analysis for claude-parser

## Current Logging State

### ✅ Good: Centralized Logger Config
- **File**: `claude_parser/infrastructure/logger_config.py`
- **Purpose**: Configures loguru to output to stderr only (prevents JSON hook conflicts)
- **Import Pattern**: `from .logger_config import logger`

### ✅ Files Already Using Centralized Logger Config (2 files)
1. `claude_parser/infrastructure/file_utils.py`
2. `claude_parser/infrastructure/message_repository.py`

### ✅ Files Using Direct Loguru Import (6 files)
1. `claude_parser/watch/async_watcher.py` - `from loguru import logger`
2. `claude_parser/watch/uuid_tracker.py` - `from loguru import logger`
3. `claude_parser/watch/sse_helpers.py` - `from loguru import logger`
4. `claude_parser/watch/true_streaming.py` - `from loguru import logger`
5. `claude_parser/application/sse_service.py` - `from loguru import logger`
6. `claude_parser/infrastructure/logger_config.py` - `from loguru import logger` (config file itself)

### 🔄 Mixed Pattern Issue
- **2 files** use centralized config: `from .logger_config import logger`
- **6 files** use direct import: `from loguru import logger`
- **Both patterns work** but should be standardized to ONE pattern

## Logging Violations to Fix

### Pattern Inconsistency
All loguru files should use the centralized logger config to ensure:
1. Consistent stderr output (prevents hook conflicts)
2. Single point of logging configuration
3. Easy to change logging behavior globally

### Recommended Solution

#### Option 1: Extend Centralized Pattern
Convert all direct loguru imports to use the centralized config:

```python
# Instead of:
from loguru import logger

# Use:
from claude_parser.infrastructure.logger_config import logger
```

#### Option 2: Global Logger Service (DDD Approach)
Create a proper domain service for logging following DDD principles:

```python
# claude_parser/domain/services/logging_service.py
from abc import ABC, abstractmethod
from loguru import logger as loguru_logger

class LoggingService(ABC):
    @abstractmethod
    def info(self, message: str, **kwargs): ...
    @abstractmethod
    def error(self, message: str, **kwargs): ...
    @abstractmethod
    def debug(self, message: str, **kwargs): ...

class LoguruLoggingService(LoggingService):
    def __init__(self):
        # Configure loguru once
        loguru_logger.remove()
        loguru_logger.add(sys.stderr, level="INFO")

    def info(self, message: str, **kwargs):
        loguru_logger.info(message, **kwargs)

    def error(self, message: str, **kwargs):
        loguru_logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs):
        loguru_logger.debug(message, **kwargs)
```

## Files Requiring Migration (6 files)

1. `claude_parser/watch/async_watcher.py`
2. `claude_parser/watch/uuid_tracker.py`
3. `claude_parser/watch/sse_helpers.py`
4. `claude_parser/watch/true_streaming.py`
5. `claude_parser/application/sse_service.py`
6. Any other files that add direct loguru imports in the future

## Total Impact

- **Current**: 8 files using logging (2 centralized + 6 direct)
- **Target**: 1 centralized logging system
- **Effort**: ~30 minutes (6 simple import changes)
- **Benefit**: Single point of logging control, consistent behavior

## Next Steps

1. Standardize on ONE logging pattern (recommend centralized)
2. Update 6 files to use centralized logger
3. Add linting rule to prevent direct loguru imports
4. Consider DDD logging service for future expansion
