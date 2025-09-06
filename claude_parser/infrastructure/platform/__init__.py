"""Platform-specific utilities for cross-platform compatibility."""

from .paths import get_claude_projects_dir, get_platform_config_dir

__all__ = ["get_claude_projects_dir", "get_platform_config_dir"]
