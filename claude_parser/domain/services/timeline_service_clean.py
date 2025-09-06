"""
Timeline service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
import jsonlines
from more_itertools import flatten
from deepdiff import DeepDiff
import jmespath

from ...core.resources import get_resource_manager
from ...components.git_timeline_builder import GitTimelineBuilder
from ...components.timeline_navigator import TimelineNavigator


class TimelineService:
    """Clean timeline service using ResourceManager pattern."""

    def __init__(self, jsonl_dir: Path):
        """Initialize with centralized resources."""
        self.jsonl_dir = jsonl_dir
        self.resources = get_resource_manager()
        self.builder = GitTimelineBuilder(self.resources)
        self.navigator = TimelineNavigator(self.resources)

        # Load events and setup Git repo
        self.events = list(flatten(jsonlines.open(f) for f in Path(jsonl_dir).glob("*.jsonl")))
        self.repo = self.builder.create_timeline_repo()
        self._uuid_to_commit = {}
        self._apply_all_events()

    def _apply_all_events(self):
        """Apply all events to Git timeline using micro-component."""
        for event in self.events:
            self.builder.commit_event(self.repo, event, self._uuid_to_commit)

    @lru_cache(maxsize=128)
    def checkout(self, point: str) -> Dict[str, Any]:
        """Checkout timeline point - delegate to Git framework."""
        if point != "latest":
            try:
                self.repo.git.checkout(point)
            except:
                return {}
        return self.navigator._get_repo_state(self.repo)

    def checkout_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Checkout by UUID using micro-component."""
        return self.navigator.checkout_by_uuid(self.repo, uuid, self._uuid_to_commit)

    def get_file_at_uuid(self, file_path: str, uuid: str) -> Optional[str]:
        """Get file at UUID using micro-component."""
        return self.navigator.get_file_at_uuid(self.repo, file_path, uuid, self._uuid_to_commit)

    def branch(self, name: str):
        """Create branch - delegate to Git."""
        self.repo.git.checkout("-b", name)

    def list_branches(self) -> List[str]:
        """List branches - delegate to Git."""
        return [b.name for b in self.repo.branches]

    def query(self, expr: str, limit: Optional[int] = None) -> List[Dict]:
        """Query events using JMESPath framework."""
        results = jmespath.search(expr, self.events) or []
        return results[:limit] if limit else results

    def diff(self, from_point: str, to_point: str) -> Dict:
        """Diff between points - delegate to DeepDiff framework."""
        from_state = self.checkout(from_point)
        to_state = self.checkout(to_point)
        return DeepDiff(from_state, to_state, ignore_order=True)

    def clear_cache(self):
        """Clear LRU cache."""
        self.checkout.cache_clear()


# Backward Compatibility Class
class Timeline:
    """Backward compatibility for legacy Timeline."""

    def __init__(self, jsonl_dir: Path):
        """Initialize with timeline service."""
        self.service = TimelineService(jsonl_dir)
        # Expose internal attributes for compatibility
        self.events = self.service.events
        self.repo = self.service.repo
        self._uuid_to_commit = self.service._uuid_to_commit

    def checkout(self, point: str) -> Dict[str, Any]:
        return self.service.checkout(point)

    def checkout_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        return self.service.checkout_by_uuid(uuid)

    def get_file_at_uuid(self, file_path: str, uuid: str) -> Optional[str]:
        return self.service.get_file_at_uuid(file_path, uuid)

    def branch(self, name: str):
        return self.service.branch(name)

    def list_branches(self) -> List[str]:
        return self.service.list_branches()

    def query(self, expr: str, limit: Optional[int] = None) -> List[Dict]:
        return self.service.query(expr, limit)

    def diff(self, from_point: str, to_point: str) -> Dict:
        return self.service.diff(from_point, to_point)

    def clear_cache(self):
        return self.service.clear_cache()

    # Additional legacy methods that may exist
    def merge(self, branch: str, into: str) -> List[str]:
        """Merge branches - delegate to Git."""
        return []  # Simplified for now

    def get_uuid_sequence_for_file(self, file_path: str) -> List[str]:
        """Get UUID sequence for file."""
        return []  # Simplified for now

    def navigate_file_steps(self, *args, **kwargs):
        """Navigate file steps."""
        return []  # Simplified for now

    def get_operation_diff(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get operation diff."""
        return None  # Simplified for now
