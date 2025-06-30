# ../common/functions.py

"""Provides commonly used functions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Package
from .constants import PLATFORM

# =============================================================================
# >> ALL
# =============================================================================
__all__ = (
    'get_link_directory_command',
    'get_link_file_command',
)


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_link_directory_command(src, dest):
    """Create a symbolic link for the given source at the given destination."""
    if PLATFORM == "windows":
        return f'mklink /J "{dest}" "{src}"'

    else:
        return f'ln -s "{src}" "{dest}"'


def get_link_file_command(src, dest):
    """Create a hard link for the given source at the given destination."""
    if PLATFORM == "windows":
        return f'cmd /c mklink "{dest}" "{src}"'

    else:
        return f'ln -s "{src}" "{dest}"'
