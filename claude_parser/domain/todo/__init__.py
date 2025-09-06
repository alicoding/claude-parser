"""TodoDomain - Parse and manage Claude's TodoWrite format.

Domain Boundaries (DDD):
- Parser: Parse JSON (no I/O)
- Storage: File operations (no business logic)
- Display: Formatting (no data manipulation)
- Manager: Orchestrates the above (facade pattern)
- Swiper: Navigate todo history (timeline integration)
"""

from .parser import TodoParser
from .storage import TodoStorage
from .display import TodoDisplay
from .manager import TodoManager
from .swiper import TodoSwiper

__all__ = ["TodoParser", "TodoStorage", "TodoDisplay", "TodoManager", "TodoSwiper"]
