"""
Factory API - 95/5 public interface using pure framework delegation.

95%: Frameworks (Polars, Rich, watchfiles, etc.) do everything
5%: Simple factory functions that configure frameworks
"""

from pathlib import Path
from typing import List, Dict, Any, AsyncGenerator, Tuple
from ..core.resources import get_resource_manager
from ..extensions.awkward_extension import ConversationArray


def analyze_conversation(file_path: str) -> Dict[str, Any]:
    """Analyze conversation - 95% Polars framework."""
    resources = get_resource_manager()
    df_ext = ConversationDataFrame(resources)

    # Load with our file loader (handles complex JSONL)
    from ..components.file_loader import FileLoader
    loader = FileLoader(resources)
    raw_messages = loader.load(file_path)

    # Convert to Polars (framework does everything)
    df = pl.DataFrame(raw_messages)

    # Analysis with Polars (framework does everything)
    token_analysis = df_ext.analyze_tokens(df)
    time_analysis = df_ext.time_analysis(df)

    return {**token_analysis, **time_analysis}


def load_conversation(file_path: str):
    """Load conversation - framework + file loader."""
    from ..components.file_loader import FileLoader
    from ..core.resources import get_resource_manager

    resources = get_resource_manager()
    loader = FileLoader(resources)
    return loader.load(file_path)


def load_many_conversations(file_paths: List[str]):
    """Load many conversations - 95% Polars framework."""
    return [load_conversation(path) for path in file_paths]


async def watch_conversation(file_path: str) -> AsyncGenerator[Tuple[List[Dict], List[Dict]], None]:
    """Watch conversation - 95% watchfiles framework."""
    import asyncio
    import watchfiles

    last_size = 0

    async for changes in watchfiles.awatch(file_path):
        current_data = load_conversation(file_path)

        if len(current_data) > last_size:
            new_messages = current_data[last_size:]
            last_size = len(current_data)
            yield current_data, new_messages


def create_timeline(directory: Path):
    """Create timeline - 95% Git + Rich framework."""
    from git import Repo
    import tempfile
    import jsonlines

    # Git framework handles everything
    repo = Repo.init(tempfile.mkdtemp())

    # Load events with jsonlines framework
    events = []
    for jsonl_file in directory.glob("*.jsonl"):
        with jsonlines.open(jsonl_file) as reader:
            events.extend(list(reader))

    # Simple timeline object
    class Timeline:
        def __init__(self, events):
            self.events = events
            self.repo = repo

    return Timeline(events)


def discover_transcripts(cwd: Path = None) -> List[str]:
    """Discover transcripts - 95% pathlib framework."""
    if cwd is None:
        cwd = Path.cwd()

    claude_projects = Path.home() / ".claude" / "projects"
    if not claude_projects.exists():
        return []

    # Let pathlib do all the work
    transcripts = []
    for project_dir in claude_projects.iterdir():
        if project_dir.is_dir():
            jsonl_files = list(project_dir.glob("*.jsonl"))
            if jsonl_files:
                # Most recent first
                jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                transcripts.extend([str(f) for f in jsonl_files])

    return transcripts
