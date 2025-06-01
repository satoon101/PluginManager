# ../common/functions.py

"""Provides commonly used functions."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
from os import system

# Package
from .constants import (
    PLATFORM,
    PLUGIN_LIST,
)


# ==============================================================================
# >> FUNCTIONS
# ==============================================================================
def clear_screen():
    """Clear the screen."""
    system("cls" if PLATFORM == "windows" else "clear")


def get_plugin(suffix, *, allow_all=True):
    """Return a plugin by name to do something with."""
    clear_screen()

    # Are there any plugins?
    if not PLUGIN_LIST:
        print(f"There are no plugins to {suffix}.")
        return None

    # Get the message to ask
    message = f"What plugin would you like to {suffix}?\n\n"
    for number, plugin in enumerate(PLUGIN_LIST, 1):
        message += f"\t({number}) {plugin}\n"

    options = list(PLUGIN_LIST)
    if allow_all:
        message += f"\t({len(PLUGIN_LIST) + 1}) ALL\n"
        options.append("ALL")

    value = None
    while True:
        try:
            value = input(message)
            choice_index = int(value)
            assert 0 < choice_index < len(options)
        except (ValueError, AssertionError):
            clear_screen()
            print(f"Invalid choice '{value}'. Please try again.")
        else:
            return list(options)[choice_index - 1]


def link_directory(src, dest):
    """Create a symbolic link for the given source at the given destination."""
    # Is this a Windows OS?
    if PLATFORM == "windows":

        # Link using Windows format
        system(f'mklink /J "{dest}" "{src}"')

    # Is this a Linux OS?
    else:

        # Link using Linux format
        system(f'ln -s "{src}" "{dest}"')


def link_file(src, dest):
    """Create a hard link for the given source at the given destination."""
    # Is this a Windows OS?
    if PLATFORM == "windows":

        # Link using Windows format
        system(f'mklink /H "{dest}" "{src}"')

    # Is this a Linux OS?
    else:

        # Link using Linux format
        system(f'ln -s "{src}" "{dest}"')


def copy_over_file(src, dest):
    if dest.is_file():
        dest.remove()
    src.copy(dest)
