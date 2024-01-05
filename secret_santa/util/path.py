"""Path utilities."""

from pathlib import Path


def get_project_root() -> Path:
    """Get the path of the project's root directory.

    Returns:
        Path of the project's root directory.

    """
    # The root directory is two levels above this file
    return Path(__file__).parent.parent.parent
