"""Test TodoSwiper - Tinder-like todo history navigation."""
import pytest
import tempfile
import orjson
from pathlib import Path
from claude_parser.domain.todo import TodoSwiper


def test_swiper_navigation():
    """Test swipe left/right through todo history."""
    # Mock todo history (newest first)
    history = [
        [{"content": "Task 3", "status": "completed"}],  # Most recent
        [{"content": "Task 2", "status": "completed"}],
        [{"content": "Task 1", "status": "completed"}]   # Oldest
    ]

    swiper = TodoSwiper(history)

    # Start at latest (index 0)
    assert swiper.current_index == 0
    current = swiper.current()
    assert "Task 3" in str(current["display"])

    # Swipe left to go back in time
    swiper.swipe_left()
    assert swiper.current_index == 1
    assert "Task 2" in str(swiper.current()["display"])

    # Swipe left again
    swiper.swipe_left()
    assert swiper.current_index == 2
    assert "Task 1" in str(swiper.current()["display"])

    # Can't go further back
    swiper.swipe_left()
    assert swiper.current_index == 2  # Stays at oldest

    # Swipe right to go forward in time
    swiper.swipe_right()
    assert swiper.current_index == 1
    assert "Task 2" in str(swiper.current()["display"])


def test_swiper_display_format():
    """Test Rich display format for swiper."""
    history = [
        [
            {"content": "Design API", "status": "completed"},
            {"content": "Test API", "status": "completed"}
        ]
    ]

    swiper = TodoSwiper(history)
    current = swiper.current()

    assert "✅ 2/2 todos completed" in str(current["display"])
    assert "☒ Design API" in str(current["display"])
    assert "☒ Test API" in str(current["display"])


def test_swiper_empty_history():
    """Handle empty todo history."""
    swiper = TodoSwiper([])
    current = swiper.current()

    assert "No todo history found" in str(current["display"])
    assert not swiper.can_swipe_left()
    assert not swiper.can_swipe_right()


def test_incremental_todo_progression():
    """Test incremental completion of SAME todos - core backlog behavior."""
    # Simulate incremental completion of same todo list
    history = [
        # Latest: all completed (3/3)
        [
            {"content": "Design API", "status": "completed", "activeForm": "Designing API"},
            {"content": "Test API", "status": "completed", "activeForm": "Testing API"},
            {"content": "Deploy API", "status": "completed", "activeForm": "Deploying API"}
        ],
        # Previous: 2/3 completed
        [
            {"content": "Design API", "status": "completed", "activeForm": "Designing API"},
            {"content": "Test API", "status": "completed", "activeForm": "Testing API"},
            {"content": "Deploy API", "status": "in_progress", "activeForm": "Deploying API"}
        ],
        # Earlier: 1/3 completed
        [
            {"content": "Design API", "status": "completed", "activeForm": "Designing API"},
            {"content": "Test API", "status": "in_progress", "activeForm": "Testing API"},
            {"content": "Deploy API", "status": "pending", "activeForm": "Deploying API"}
        ],
        # Initial: 0/3 completed
        [
            {"content": "Design API", "status": "pending", "activeForm": "Designing API"},
            {"content": "Test API", "status": "pending", "activeForm": "Testing API"},
            {"content": "Deploy API", "status": "pending", "activeForm": "Deploying API"}
        ]
    ]

    swiper = TodoSwiper(history)

    # Current: 3/3 completed
    current = swiper.current()
    assert "✅ 3/3 todos completed" in str(current["display"])
    assert all(t["status"] == "completed" for t in current["todos"])

    # Swipe back: 2/3 completed
    swiper.swipe_left()
    current = swiper.current()
    assert "⏳ 2/3 todos completed" in str(current["display"])
    completed_count = sum(1 for t in current["todos"] if t["status"] == "completed")
    assert completed_count == 2

    # Swipe back: 1/3 completed
    swiper.swipe_left()
    current = swiper.current()
    assert "⏳ 1/3 todos completed" in str(current["display"])
    completed_count = sum(1 for t in current["todos"] if t["status"] == "completed")
    assert completed_count == 1

    # Swipe back: 0/3 completed
    swiper.swipe_left()
    current = swiper.current()
    assert "⏳ 0/3 todos completed" in str(current["display"])
    completed_count = sum(1 for t in current["todos"] if t["status"] == "completed")
    assert completed_count == 0


def test_content_similarity_grouping():
    """Test content similarity algorithm groups same todos correctly."""
    # Test data: overlapping content should group together
    snapshots = [
        # Same project, different completion states
        [{"content": "Task A"}, {"content": "Task B"}, {"content": "Task C"}],
        [{"content": "Task A"}, {"content": "Task B"}],  # Same project, fewer tasks
        [{"content": "Task A"}, {"content": "Task B"}, {"content": "Task C"}, {"content": "Task D"}],  # Same project, more tasks

        # Different project
        [{"content": "Different Task X"}, {"content": "Different Task Y"}]
    ]

    grouped = TodoSwiper._group_by_content_similarity(snapshots)

    # Should create groups based on >50% content similarity
    assert len(grouped) >= 2  # At least separate groups

    # First group should be the largest (sorted by length)
    main_timeline = grouped[0]
    assert len(main_timeline) >= 2  # Multiple related snapshots

    # Different project should be in a separate group
    different_project_found = any(
        any("Different Task X" in str(snapshot) for snapshot in timeline)
        for timeline in grouped
    )
    assert different_project_found  # Must find the different project in some group


def test_transcript_parsing_integration():
    """Test full transcript parsing with realistic TodoWrite data."""
    # Create temporary transcript file with realistic TodoWrite messages
    transcript_data = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Setup project", "status": "pending", "activeForm": "Setting up project"},
                                {"content": "Write tests", "status": "pending", "activeForm": "Writing tests"}
                            ]
                        }
                    }
                ]
            }
        },
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Setup project", "status": "completed", "activeForm": "Setting up project"},
                                {"content": "Write tests", "status": "in_progress", "activeForm": "Writing tests"}
                            ]
                        }
                    }
                ]
            }
        },
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Setup project", "status": "completed", "activeForm": "Setting up project"},
                                {"content": "Write tests", "status": "completed", "activeForm": "Writing tests"}
                            ]
                        }
                    }
                ]
            }
        }
    ]

    # Write to temporary transcript file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.jsonl') as f:
        for entry in transcript_data:
            f.write(orjson.dumps(entry) + b'\n')
        temp_path = f.name

    try:
        # Test from_transcript parsing
        swiper = TodoSwiper.from_transcript(temp_path)

        # Should have 3 snapshots showing progression
        assert len(swiper.history) == 3

        # Latest: both completed
        current = swiper.current()
        assert "✅ 2/2 todos completed" in str(current["display"])

        # Previous: 1 completed, 1 in progress
        swiper.swipe_left()
        current = swiper.current()
        assert "⏳ 1/2 todos completed" in str(current["display"])

        # Earliest: both pending
        swiper.swipe_left()
        current = swiper.current()
        assert "⏳ 0/2 todos completed" in str(current["display"])

    finally:
        # Cleanup
        Path(temp_path).unlink()


def test_content_overlap_calculation():
    """Test content overlap calculation for grouping decisions."""
    # Test edge cases for content similarity
    snapshots = [
        # 100% overlap
        [{"content": "Task A"}, {"content": "Task B"}],
        [{"content": "Task A"}, {"content": "Task B"}],

        # 50% overlap (should group)
        [{"content": "Task A"}, {"content": "Task B"}],
        [{"content": "Task A"}, {"content": "Task C"}],

        # 25% overlap (should NOT group)
        [{"content": "Task A"}, {"content": "Task B"}, {"content": "Task C"}, {"content": "Task D"}],
        [{"content": "Task A"}],

        # 0% overlap (should NOT group)
        [{"content": "Task X"}, {"content": "Task Y"}]
    ]

    grouped = TodoSwiper._group_by_content_similarity(snapshots)

    # Should create separate groups based on >50% threshold
    # Groups: [100% + 50%], [25%], [0%]
    assert len(grouped) >= 2  # At least separate high/low overlap groups

    # Largest group should contain the high-overlap snapshots
    main_group = grouped[0]
    assert len(main_group) >= 3  # 100% + 50% overlap snapshots


def test_backlog_system_integration():
    """Test TodoSwiper integration with backlog workflows - critical for production."""
    # Simulate realistic backlog scenario: epic broken down into tasks
    epic_progression = [
        # Final state: Epic complete
        [
            {"content": "Research libraries", "status": "completed", "activeForm": "Researching libraries"},
            {"content": "Design architecture", "status": "completed", "activeForm": "Designing architecture"},
            {"content": "Implement core features", "status": "completed", "activeForm": "Implementing core features"},
            {"content": "Write comprehensive tests", "status": "completed", "activeForm": "Writing comprehensive tests"},
            {"content": "Deploy to production", "status": "completed", "activeForm": "Deploying to production"}
        ],
        # Mid-development: Testing phase
        [
            {"content": "Research libraries", "status": "completed", "activeForm": "Researching libraries"},
            {"content": "Design architecture", "status": "completed", "activeForm": "Designing architecture"},
            {"content": "Implement core features", "status": "completed", "activeForm": "Implementing core features"},
            {"content": "Write comprehensive tests", "status": "in_progress", "activeForm": "Writing comprehensive tests"},
            {"content": "Deploy to production", "status": "pending", "activeForm": "Deploying to production"}
        ],
        # Early development: Implementation phase
        [
            {"content": "Research libraries", "status": "completed", "activeForm": "Researching libraries"},
            {"content": "Design architecture", "status": "completed", "activeForm": "Designing architecture"},
            {"content": "Implement core features", "status": "in_progress", "activeForm": "Implementing core features"},
            {"content": "Write comprehensive tests", "status": "pending", "activeForm": "Writing comprehensive tests"},
            {"content": "Deploy to production", "status": "pending", "activeForm": "Deploying to production"}
        ]
    ]

    swiper = TodoSwiper(epic_progression)

    # Verify backlog progression tracking
    progress_snapshots = []

    for i in range(len(epic_progression)):
        swiper.current_index = i
        current = swiper.current()
        completed = sum(1 for t in current["todos"] if t["status"] == "completed")
        total = len(current["todos"])
        progress_snapshots.append(f"{completed}/{total}")

    # Should show clear progression: 5/5 -> 3/5 -> 2/5
    assert progress_snapshots == ["5/5", "3/5", "2/5"]

    # Verify can navigate through entire epic timeline
    # Start at index 0 (latest), should be able to swipe left to older snapshots
    swiper.current_index = 0  # Reset to start
    assert swiper.can_swipe_left()  # Can go to index 1
    swiper.swipe_left()
    assert swiper.can_swipe_left()  # Can go to index 2
    swiper.swipe_left()
    assert not swiper.can_swipe_left()  # At index 2, can't go further (length=3)
