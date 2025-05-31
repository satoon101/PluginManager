# ../plugin_checker.py

"""Checks plugins for standards issues."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
from os import system

# Package
from common.constants import PLUGIN_LIST, START_DIR, config
from common.functions import clear_screen, get_plugin


# ==============================================================================
# >> MAIN FUNCTION
# ==============================================================================
def check_plugin(plugin_name):
    """Check the given plugin for standards issues."""
    # Get the plugin's path
    plugin_path = START_DIR.joinpath(
        plugin_name,
        config["PLUGIN_BASE_PATH"],
        plugin_name,
    )

    system(f"ruff check {plugin_path}")


# ==============================================================================
# >> CALL MAIN FUNCTION
# ==============================================================================
if __name__ == "__main__":

    # Get the plugin to check
    _plugin_name = get_plugin("check")
    if _plugin_name is not None:

        clear_screen()
        if _plugin_name == "ALL":
            for _plugin_name in PLUGIN_LIST:
                print(f'Checking plugin "{_plugin_name}"')
                check_plugin(_plugin_name)

        else:
            check_plugin(_plugin_name)
