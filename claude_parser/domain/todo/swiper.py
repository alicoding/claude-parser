"""TodoSwiper - Tinder-like navigation through todo history."""
from typing import Dict, List

from rich.console import Console

from .display import TodoDisplay


class TodoSwiper:
    """Swipe through todo history like Tinder."""

    def __init__(self, history: List[List[Dict]]):
        """Initialize with todo history (newest first)."""
        self.history = history
        self.current_index = 0
        self.console = Console()

    def swipe_left(self) -> bool:
        """Swipe left = go back in time (older todos)."""
        if self.can_swipe_left():
            self.current_index += 1
            return True
        return False

    def swipe_right(self) -> bool:
        """Swipe right = go forward in time (newer todos)."""
        if self.can_swipe_right():
            self.current_index -= 1
            return True
        return False

    def can_swipe_left(self) -> bool:
        """Can we go back further in history?"""
        return self.current_index < len(self.history) - 1

    def can_swipe_right(self) -> bool:
        """Can we go forward in history?"""
        return self.current_index > 0

    def current(self) -> Dict:
        """Get current todo snapshot with metadata."""
        if not self.history:
            return {
                "display": "📋 No todo history found",
                "timestamp": None,
                "position": "0/0",
            }

        todos = self.history[self.current_index]
        total = len(self.history)
        position = self.current_index + 1

        # Build Rich display
        tree = TodoDisplay.build_tree(todos)
        progress = TodoDisplay.calculate_progress(todos)

        # Add completion status
        if progress["completed"] == progress["total"]:
            status = f"✅ {progress['completed']}/{progress['total']} todos completed"
        else:
            status = f"⏳ {progress['completed']}/{progress['total']} todos completed"

        # Render tree to string using Rich console
        from io import StringIO

        from rich.console import Console

        string_io = StringIO()
        temp_console = Console(file=string_io, width=80)
        temp_console.print(tree)
        tree_text = string_io.getvalue()

        # Combine status and tree for display
        display_text = f"{status}\n{tree_text}"

        return {
            "display": display_text,
            "status": status,
            "position": f"{position}/{total}",
            "todos": todos,
            "progress": progress,
            "navigation": {
                "can_swipe_left": self.can_swipe_left(),
                "can_swipe_right": self.can_swipe_right(),
            },
        }

    def show(self):
        """Display current snapshot with Rich."""
        current = self.current()

        # Create panel with navigation hints
        nav_hints = []
        if current["navigation"]["can_swipe_left"]:
            nav_hints.append("← Swipe left for older")
        if current["navigation"]["can_swipe_right"]:
            nav_hints.append("→ Swipe right for newer")

        nav_text = " | ".join(nav_hints) if nav_hints else "End of history"

        # Use Rich console to print tree directly
        self.console.print(f"\n📱 Todo History - {current['position']}")

        # Print the tree (which is already Rich formatted)
        tree = TodoDisplay.build_tree(current["todos"])
        self.console.print(tree)

        # Print status and navigation
        self.console.print(f"\n{current['status']}")
        if nav_text != "End of history":
            self.console.print(f"💡 {nav_text}")

    def interactive(self):
        """Interactive swiper mode."""
        self.console.print("📱 Todo Swiper - Use ← → keys to navigate (q to quit)")

        while True:
            self.show()

            try:
                key = input("\nNavigation (←/→/q): ").strip().lower()

                if key in ["q", "quit", "exit"]:
                    break
                elif key in ["<", "left", "←"]:
                    if not self.swipe_left():
                        self.console.print("🚫 Already at oldest todos")
                elif key in [">", "right", "→"]:
                    if not self.swipe_right():
                        self.console.print("🚫 Already at newest todos")
                else:
                    self.console.print("Use ←/→ to navigate or 'q' to quit")

            except KeyboardInterrupt:
                break

        self.console.print("\n👋 Thanks for swiping!")

    @staticmethod
    def from_transcript(transcript_path: str) -> "TodoSwiper":
        """Create swiper from transcript file - shows progression of SAME todos."""
        import orjson

        all_snapshots = []

        with open(transcript_path, "rb") as f:
            for line in f:
                try:
                    data = orjson.loads(line)

                    # Look for TodoWrite in assistant messages
                    if (
                        data.get("type") == "assistant"
                        and "message" in data
                        and "content" in data["message"]
                    ):
                        for content_item in data["message"]["content"]:
                            if (
                                content_item.get("type") == "tool_use"
                                and content_item.get("name") == "TodoWrite"
                                and "input" in content_item
                            ):
                                todos = content_item["input"].get("todos", [])
                                if todos:  # Only add non-empty snapshots
                                    all_snapshots.append(todos)

                except (orjson.JSONDecodeError, KeyError):
                    continue

        # Group by content similarity to track progression of SAME todos
        grouped_timelines = TodoSwiper._group_by_content_similarity(all_snapshots)

        # Return the longest/most recent timeline (newest first)
        if grouped_timelines:
            return TodoSwiper(list(reversed(grouped_timelines[0])))

        return TodoSwiper([])

    @staticmethod
    def _group_by_content_similarity(snapshots):
        """Group snapshots by content similarity to track same todo progression."""
        if not snapshots:
            return []

        # Find snapshots with overlapping content (same todos in different completion states)
        timelines = []

        for snapshot in snapshots:
            # Extract just the content strings for comparison
            contents = {todo["content"] for todo in snapshot}

            # Try to find existing timeline with overlapping content
            matched_timeline = None
            for timeline in timelines:
                if timeline:  # Check if timeline is not empty
                    last_snapshot = timeline[-1]
                    last_contents = {todo["content"] for todo in last_snapshot}

                    # If >50% content overlap, it's the same todo list progression
                    overlap = len(contents & last_contents) / max(
                        len(contents), len(last_contents)
                    )
                    if overlap > 0.5:
                        matched_timeline = timeline
                        break

            if matched_timeline is not None:
                matched_timeline.append(snapshot)
            else:
                timelines.append([snapshot])

        # Sort by length (longest timeline = main progression)
        return sorted(timelines, key=len, reverse=True)
