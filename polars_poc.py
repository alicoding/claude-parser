#!/usr/bin/env python3
"""
Polars proof-of-concept for instant cg status.
This demonstrates how to replace 599-line ClaudeCodeTimeline with ~15 lines.
"""

import polars as pl
from pathlib import Path
import time

def fast_status(project_path: Path):
    """Ultra-fast status using existing data extraction + Polars analysis."""
    start_time = time.time()

    # Use existing discovery to find operations - this is what we'll optimize next
    from claude_parser.infrastructure.discovery import ConfigurableProjectDiscovery
    from claude_parser.domain.services import ClaudeCodeTimeline

    # Just to get the raw operations data (will replace this next)
    discovery = ConfigurableProjectDiscovery()
    timeline = ClaudeCodeTimeline(project_path, discovery)

    print(f"📊 Total operations: {len(timeline.tool_operations)}")

    # Convert to Polars DataFrame - this is the key optimization!
    df = pl.DataFrame(timeline.tool_operations)

    # Get file operations only (Write, Edit, MultiEdit) - blazing fast filtering
    file_ops = df.filter(
        pl.col("tool_name").is_in(["Write", "Edit", "MultiEdit"]) &
        pl.col("file_path").is_not_null()
    )

    print(f"📝 File operations: {file_ops.height}")

    # Count operations per file - vectorized groupby
    file_counts = (
        file_ops
        .with_columns(
            pl.col("file_path").map_elements(
                lambda x: Path(x).name if x else "unknown",
                return_dtype=pl.Utf8
            ).alias("filename")
        )
        .group_by("filename")
        .agg(pl.count().alias("operations"))
        .sort("operations", descending=True)
    )

    print("📄 Files modified:")
    for row in file_counts.iter_rows(named=True):
        print(f"  {row['filename']}: {row['operations']} operations")

    # Count operations per session - also vectorized
    session_counts = (
        file_ops
        .group_by("sessionId")
        .agg(pl.count().alias("operations"))
        .sort("operations", descending=True)
    )

    if session_counts.height > 1:
        print(f"🔀 Multi-session detected ({session_counts.height} sessions):")
        for row in session_counts.head(5).iter_rows(named=True):
            session_id = row["sessionId"]
            short_id = session_id[:8] if session_id else "unknown"
            print(f"  📋 Session {short_id}: {row['operations']} operations")

    # Clean up timeline resources
    timeline.clear_cache()

    elapsed = time.time() - start_time
    print(f"⚡ Completed in {elapsed:.3f}s (vs 8+ seconds before)")
    print("📈 Next: Replace ClaudeCodeTimeline data loading with direct JSONL→DataFrame")


if __name__ == "__main__":
    fast_status(Path.cwd())
