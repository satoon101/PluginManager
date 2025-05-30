# ../{{ plugin_name }}/strings.py

"""Contains all translation variables for the base plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from translations.strings import LangStrings

# Plugin
from .info import info

# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    "CONFIG_STRINGS",
)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CONFIG_STRINGS = LangStrings(info.name)
