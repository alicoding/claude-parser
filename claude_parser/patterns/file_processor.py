"""
File processor to eliminate duplication in file processing logic.

This addresses the DRY violation in verify_spec_v2.py where
file processing logic is duplicated multiple times.
"""

from pathlib import Path
from typing import List, Optional
from toolz import pipe, concat
from toolz.curried import filter as toolz_filter


class FileProcessor:
    """
    Generic file processor following 95/5 principle.
    
    Eliminates duplication found in:
    - verify_spec_v2.py: get_python_files()
    - Multiple similar file processing patterns
    """
    
    def __init__(self, patterns: List[str], exclusions: Optional[List[str]] = None):
        """
        Initialize processor with file patterns and exclusions.
        
        Args:
            patterns: List of glob patterns (e.g., ['*.py', '*.pyi'])
            exclusions: List of path fragments to exclude
        """
        self.patterns = patterns
        self.exclusions = exclusions or []
    
    def process(self, base_path: str) -> List[Path]:
        """
        Process files using toolz pipeline.
        
        Args:
            base_path: Directory to search in
            
        Returns:
            List of Path objects matching patterns and not excluded
        """
        return pipe(
            self._get_files(base_path),
            toolz_filter(lambda p: not self._is_excluded(p)),
            list
        )
    
    def _get_files(self, base_path: str) -> List[Path]:
        """Get all files matching patterns."""
        base = Path(base_path)
        
        if not base.exists():
            return []
        
        # Collect files for all patterns
        files = []
        for pattern in self.patterns:
            files.extend(base.rglob(pattern))
        
        return files
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if path contains any excluded pattern."""
        path_str = str(path)
        return any(exc in path_str for exc in self.exclusions)


# Convenience function for backward compatibility
def get_python_files(base_path: str, exclusions: Optional[List[str]] = None) -> List[Path]:
    """
    Get Python files from a directory - backward compatible wrapper.
    
    This maintains the original API while using FileProcessor internally.
    """
    default_exclusions = [
        'node_modules', '.venv', 'venv', '__pycache__',
        '.pytest_cache', 'research', 'verify_spec.py'
    ]
    
    if exclusions:
        default_exclusions.extend(exclusions)
    
    processor = FileProcessor(['*.py'], default_exclusions)
    return processor.process(base_path)