# ../plugin_linker.py

"""Links plugins to Source.Python's repository."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from path import Path

# Package
from common.constants import (
    LINK_BASE_DIR,
    START_DIR,
    PLUGIN_LIST,
    config,
)
from common.functions import get_link_directory_command, get_link_file_command
from common.interface import BaseInterface


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Plugin Linker"

    def run(self):
        self.window.title(self.name)
        self.clear_grid()
        self.create_grid(data=PLUGIN_LIST)
        self.add_back_button(self.on_back_to_main)

    def on_click(self, option):
        self.clear_grid()
        console = self.get_console()
        commands = self.get_all_link_commands(option)
        self.execute_console_commands(
            console=console,
            commands=commands,
        )
        self.add_back_button(self.run)

    def get_all_link_commands(self, plugin_name):
        commands = []
        for path, extensions in {
            config["CONFIG_BASE_PATH"]: ['cfg', 'ini'],
            config["DATA_BASE_PATH"]: ['ini', 'json'],
            config["DOCS_BASE_PATH"]: [],
            config["EVENTS_BASE_PATH"]: [],
            config["LOGS_BASE_PATH"]: [],
            config["PLUGIN_BASE_PATH"]: [],
            config["SOUND_BASE_PATH"]: ['mp3', 'wav'],
            config["TRANSLATIONS_BASE_PATH"]: [],
        }.items():
            commands.extend(
                self.get_link_commands(
                    plugin_name,
                    path,
                    extensions=extensions,
                )
            )

        translations_path = Path(config["TRANSLATIONS_BASE_PATH"])
        for values in config["CONDITIONAL_PYTHON_FILES"].values():
            path = values.get("translations_file_path")
            if not path:
                continue

            commands.extend(
                self.get_link_commands(
                    plugin_name,
                    translations_path / path,
                    extensions=["ini"],
                )
            )

        for path in config["CONDITIONAL_PATHS"].values():
            if not path.startswith(translations_path):
                continue

            commands.extend(
                self.get_link_commands(
                    plugin_name,
                    path,
                )
            )

        return commands

    @staticmethod
    def get_link_commands(plugin_name, *args, extensions=None):
        """Link the directory using the given arguments."""
        extensions = extensions or []
        plugin_path = START_DIR / plugin_name
        src = plugin_path.joinpath(*args, plugin_name)

        # Link the directory?
        if src.is_dir():
            dest = LINK_BASE_DIR.joinpath(*args, plugin_name)
            if not dest.is_dir():
                yield get_link_directory_command(src, dest)

        for extension in extensions:
            new_src = src + f".{extension}"
            if new_src.is_file():
                dest = LINK_BASE_DIR.joinpath(*args, plugin_name) + f".{extension}"
                if not dest.is_file():
                    yield get_link_file_command(new_src, dest)
