# ../plugin_linker.py

"""Links plugins to Source.Python's repository."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
from path import Path

# Package
from common.constants import (
    LINK_BASE_DIR,
    START_DIR,
    PLUGIN_LIST,
    config,
)
from common.functions import clear_screen, get_plugin, link_directory, link_file


# ==============================================================================
# >> MAIN FUNCTION
# ==============================================================================
def link_plugin(plugin_name):
    """Link the given plugin name to Source.Python's repository."""
    for path in (
        config["CONFIG_BASE_PATH"],
        config["DATA_BASE_PATH"],
        config["DOCS_BASE_PATH"],
        config["EVENTS_BASE_PATH"],
        config["LOGS_BASE_PATH"],
        config["PLUGIN_BASE_PATH"],
        config["SOUND_BASE_PATH"],
        config["TRANSLATIONS_BASE_PATH"],
    ):
        _link_directory_or_files(
            plugin_name,
            path,
        )

    translations_path = Path(config["TRANSLATIONS_BASE_PATH"])
    for values in config["CONDITIONAL_PYTHON_FILES"].values():
        path = values.get("translations_file_path")
        if not path:
            continue

        _link_directory_or_files(
            plugin_name,
            translations_path / path,
        )

    for path in config["CONDITIONAL_PATHS"].values():
        if not path.startswith(translations_path):
            continue

        _link_directory_or_files(
            plugin_name,
            path,
        )


# ==============================================================================
# >> HELPER FUNCTIONS
# ==============================================================================
def _link_directory_or_files(plugin_name, *args):
    """Link the directory using the given arguments."""
    plugin_path = START_DIR / plugin_name
    src = plugin_path.joinpath(*args, plugin_name)

    # Link the directory?
    if src.is_dir():
        dest = LINK_BASE_DIR.joinpath(*args, plugin_name)
        if not dest.is_dir():
            link_directory(src, dest)

    src += '.ini'
    if src.is_file():
        dest = LINK_BASE_DIR.joinpath(*args, plugin_name) + '.ini'
        if not dest.is_file():
            link_file(src, dest)


# ==============================================================================
# >> MAIN FUNCTION
# ==============================================================================
def run():
    plugin_name = get_plugin("link")

    # Was a valid plugin chosen?
    if plugin_name is not None:
        clear_screen()
        if plugin_name == "ALL":
            for plugin_name in PLUGIN_LIST:
                link_plugin(plugin_name)
        else:
            link_plugin(plugin_name)


if __name__ == "__main__":
    run()
