# ../plugin_checker.py

"""Checks plugins for standards issues."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import sys

# Package
from common.constants import PLUGIN_LIST, START_DIR, config
from common.interface import BaseInterface


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Plugin Checker"
    stdout = sys.stdout
    stderr = sys.stderr

    def run(self):
        self.window.tite = self.name
        self.clear_grid()
        self.create_grid(data=PLUGIN_LIST)
        self.add_back_button(self.on_back_to_main)

    def on_click(self, option):
        self.clear_grid()
        plugin_path = START_DIR.joinpath(
            option,
            config["PLUGIN_BASE_PATH"],
            option,
        )
        self.create_console_output(
            commands=[f"ruff check {plugin_path}"],
        )
        self.add_back_button(self.run)
