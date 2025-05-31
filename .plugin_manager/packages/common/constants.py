# ../common/constants.py

"""Provides commonly used constants."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
import os
import sys
from collections import ChainMap
from platform import system

# Site-Package
from configobj import ConfigObj
from path import Path


# ==============================================================================
# >> BASE VARIABLES
# ==============================================================================
PLATFORM = system().lower()

# Store the binary names
_binary = "dll" if PLATFORM == "windows" else "so"
SOURCE_BINARY = f"source-python.{_binary}"
CORE_BINARY = f"core.{_binary}"

# Store the Path based configuration values
START_DIR = Path(os.environ["STARTDIR"])
config = dict(ChainMap(*ConfigObj(START_DIR / 'config.ini').values()))

_command = Path(sys.argv[0]).stem
_disabled_commands = config["DISABLED_COMMANDS"]
if isinstance(_disabled_commands, str):
    _disabled_commands = [_disabled_commands]
if _command in config["DISABLED_COMMANDS"]:
    msg = f"Command '{_command}' is disabled."
    raise ValueError(msg)

PLUGIN_PRIMARY_FILES_DIR = START_DIR / ".files/plugin_primary_files"
PLUGIN_REPO_ROOT_FILES_DIR = START_DIR / ".files/plugin_repo_root_files"
CONDITIONAL_PYTHON_FILES_DIR = START_DIR / ".files/conditional_python_files"

LINK_BASE_DIR = Path(config["LINK_BASE_DIRECTORY"])
RELEASE_DIR = Path(config["RELEASE_DIRECTORY"])

# Get a list of all plugins
PLUGIN_LIST = [
    x.stem for x in START_DIR.dirs()
    if not x.stem.startswith((".", "_"))
]
