"""Cross-platform path resolution following XDG and Windows AppData conventions."""

import os
import sys
from pathlib import Path
from typing import Optional


def get_platform_config_dir() -> Path:
    """Get the platform-appropriate configuration directory.

    Follows industry standards:
    - Linux/macOS: XDG Base Directory Specification (~/.config or $XDG_CONFIG_HOME)
    - Windows: %APPDATA% directory
    - Docker/Containers: Respects mounted volumes and custom $HOME

    Returns:
        Platform-appropriate configuration directory path.
    """
    if sys.platform == "win32":
        # Windows: Use %APPDATA% (roaming) for config
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata)
        # Fallback to user profile if APPDATA not set
        return Path.home() / "AppData" / "Roaming"
    else:
        # Linux/macOS: Follow XDG Base Directory Specification
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            return Path(xdg_config_home)
        # Default XDG location
        return Path.home() / ".config"


def get_claude_projects_dir(override_env_var: str = "CLAUDE_PROJECTS_DIR") -> Path:
    """Get the Claude Code projects directory with environment variable override.

    Priority order:
    1. CLAUDE_PROJECTS_DIR environment variable (highest priority)
    2. Platform-specific config directory + 'claude/projects'
    3. Fallback to ~/.claude/projects for backward compatibility

    This design supports:
    - User configuration: export CLAUDE_PROJECTS_DIR=/custom/path
    - CI/CD testing: CLAUDE_PROJECTS_DIR=/tmp/test-projects
    - Docker containers: Volume mounts or custom paths
    - Corporate environments: Restricted home directories
    - Cloud IDEs: Workspace-specific paths

    Args:
        override_env_var: Environment variable name for override (for testing).

    Returns:
        Path to Claude Code projects directory.

    Examples:
        # Default behavior
        get_claude_projects_dir()
        # -> Windows: %APPDATA%/Claude/projects
        # -> Linux: ~/.config/claude/projects

        # With environment override
        os.environ['CLAUDE_PROJECTS_DIR'] = '/workspace/claude-projects'
        get_claude_projects_dir()
        # -> /workspace/claude-projects

        # In Docker with volume mount
        # docker run -v $HOME/.claude:/root/.config/claude ...
        # -> /root/.config/claude/projects
    """
    # 1. Check for explicit override (highest priority)
    if override_path := os.environ.get(override_env_var):
        return Path(override_path).expanduser().resolve()

    # 2. Use platform-appropriate config directory
    try:
        config_dir = get_platform_config_dir()
        # Windows uses title case for app directories, Unix uses lowercase
        app_dir = "Claude" if sys.platform == "win32" else "claude"
        return config_dir / app_dir / "projects"
    except Exception:
        # 3. Fallback for any platform detection issues
        return Path.home() / ".claude" / "projects"


def ensure_claude_projects_dir(projects_dir: Optional[Path] = None) -> Path:
    """Ensure the Claude projects directory exists and is accessible.

    Args:
        projects_dir: Optional custom projects directory.

    Returns:
        Path to projects directory (created if necessary).

    Raises:
        PermissionError: If directory cannot be created or accessed.
        OSError: If filesystem operations fail.
    """
    if projects_dir is None:
        projects_dir = get_claude_projects_dir()

    # Create directory if it doesn't exist
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Verify we can read the directory
    if not projects_dir.is_dir():
        raise OSError(f"Projects directory is not a directory: {projects_dir}")

    if not os.access(projects_dir, os.R_OK):
        raise PermissionError(f"Cannot read projects directory: {projects_dir}")

    return projects_dir
