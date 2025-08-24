"""
Timeline - Ultra minimal using maximum libraries.
Every operation delegates to a library.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any, List
import jsonlines
from git import Repo
from git.exc import GitCommandError
import jmespath
from deepdiff import DeepDiff
from functools import lru_cache
from more_itertools import flatten


class Timeline:
    """Pure delegation to libraries - almost no custom logic."""
    
    def __init__(self, jsonl_dir: Path):
        self.events = list(flatten(
            jsonlines.open(f) for f in Path(jsonl_dir).glob("*.jsonl")
        ))
        self.repo = Repo.init(tempfile.mkdtemp())
        self._setup_git()
        self._apply_all()
    
    def _setup_git(self):
        config = self.repo.config_writer()
        config.set_value("user", "name", "Timeline").release()
        config.set_value("user", "email", "t@c.ai").release()
    
    def _apply_all(self):
        for e in self.events:
            self._commit_event(e)
    
    def _commit_event(self, e: Dict):
        if not (path := e.get('file_path')):
            return
        
        file = Path(self.repo.working_dir) / path
        file.parent.mkdir(parents=True, exist_ok=True)
        
        # Delegate to pathlib and git
        if e.get('tool_name') == 'Write':
            file.write_text(e.get('content', ''))
        elif e.get('tool_name') in ('Edit', 'MultiEdit'):
            edits = e.get('edits', [{'old_string': e.get('old_string'), 
                                     'new_string': e.get('new_string')}])
            if file.exists():
                text = file.read_text()
                for edit in edits:
                    text = text.replace(edit['old_string'], edit['new_string'], 1)
                file.write_text(text)
        
        self.repo.index.add([str(file)])
        self.repo.index.commit(f"{e.get('tool_name')} {path}")
    
    @lru_cache(maxsize=128)
    def checkout(self, point: str) -> Dict[str, Any]:
        # Delegate to git
        if point != "latest":
            try:
                self.repo.git.checkout(point.replace("branch:", ""))
            except GitCommandError:
                # Search commits
                for c in self.repo.iter_commits():
                    if point in str(c):
                        self.repo.git.checkout(c)
                        break
        
        # Delegate to pathlib
        return {
            str(p.relative_to(self.repo.working_dir)): {
                'content': p.read_text(),
                'timestamp': str(self.repo.head.commit.committed_datetime)
            }
            for p in Path(self.repo.working_dir).rglob("*")
            if p.is_file() and '.git' not in str(p)
        }
    
    def branch(self, name: str):
        self.repo.create_head(name)
    
    def list_branches(self) -> List[str]:
        return [b.name for b in self.repo.branches]
    
    def merge(self, branch: str, into: str) -> List[str]:
        try:
            self.repo.git.checkout(into)
            self.repo.git.merge(branch)
            return []
        except GitCommandError as e:
            return [str(e)]
    
    def diff(self, from_point: str, to_point: str) -> Dict:
        return DeepDiff(
            self.checkout(from_point),
            self.checkout(to_point)
        ).to_dict()
    
    def query(self, expr: str, limit: int = None) -> List[Dict]:
        data = [
            {'sha': c.hexsha, 'message': c.message, 
             'files': list(c.stats.files.keys())}
            for c in self.repo.iter_commits()
        ]
        results = jmespath.search(expr, data) or []
        return results[:limit] if limit else results
    
    def clear_cache(self):
        import shutil
        shutil.rmtree(self.repo.working_dir, ignore_errors=True)