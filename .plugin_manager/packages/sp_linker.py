# ../sp_linker.py

"""Links Source.Python's repository to games/servers."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Site-package
from configobj import ConfigObj
from path import Path

# Package
from common.constants import (
    PLATFORM,
    START_DIR,
    config,
)
from common.functions import get_link_directory_command, get_link_file_command
from common.interface import BaseInterface

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_binary = "dll" if PLATFORM == "windows" else "so"
SOURCE_BINARY = f"source-python.{_binary}"
CORE_BINARY = f"core.{_binary}"
SOURCE_PYTHON_DIR = Path(config["SOURCE_PYTHON_DIRECTORY"])
SOURCE_PYTHON_ADDONS_DIR = SOURCE_PYTHON_DIR / "addons" / "source-python"
SOURCE_PYTHON_BUILDS_DIR = SOURCE_PYTHON_DIR.joinpath(
    "src",
    "Builds",
    "Windows" if PLATFORM == "windows" else "Linux",
)
source_python_directories = {
    x.stem for x in SOURCE_PYTHON_DIR.dirs()
    if not x.stem.startswith((".", "_")) and
    x.stem not in ("addons", "src")
}


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Source.Python Linker"

    def run(self):
        self.window.tite = self.name
        self.clear_grid()
        self.create_grid(data=supported_games)
        self.add_back_button(self.on_back_to_main)

    def on_click(self, option):
        self.clear_grid()
        commands = self.get_all_link_commands(option)
        self.create_console_output(commands)
        self.add_back_button(self.run)

    @staticmethod
    def get_all_link_commands(option):
        commands = []
        path = supported_games[option]["directory"]
        branch = supported_games[option]["branch"]
        for dir_name in source_python_directories:
            directory = path / dir_name
            if not directory.is_dir():
                directory.makedirs()

            sp_dir = directory / "source-python"
            if sp_dir.is_dir():
                continue

            commands.append(
                get_link_directory_command(
                    src=SOURCE_PYTHON_DIR / dir_name / "source-python",
                    dest=sp_dir,
                )
            )

        server_addons = path / "addons" / "source-python"
        server_addons_bin = server_addons / "bin"
        if not server_addons_bin.is_dir():
            server_addons_bin.makedirs()

        for dir_name in SOURCE_PYTHON_ADDONS_DIR.dirs():
            directory = server_addons / dir_name.stem
            if directory.is_dir():
                continue

            commands.append(
                get_link_directory_command(
                    src=dir_name,
                    dest=directory,
                )
            )

        vdf = path / "addons" / "source-python.vdf"
        if not vdf.is_file():
            SOURCE_PYTHON_DIR.joinpath("addons", "source-python.vdf").copy(vdf)

        build_dir = SOURCE_PYTHON_BUILDS_DIR / branch
        if PLATFORM == "windows":
            build_dir = build_dir / "Release"

        for src, dest in (
            (build_dir / SOURCE_BINARY, path / "addons" / SOURCE_BINARY),
            (build_dir / CORE_BINARY, server_addons_bin / CORE_BINARY)
        ):
            if src.is_file() and not dest.is_file():
                print(3, src, dest)
                commands.append(
                    get_link_file_command(
                        src=src,
                        dest=dest,
                    )
                )

        return commands


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_supported_games():
    games = {}
    server_directories = config["SERVER_DIRECTORIES"]
    if isinstance(server_directories, str):
        server_directories = [server_directories]

    _check_files = ["srcds.exe", "srcds_run", "srcds_linux"]
    _support = ConfigObj(
        START_DIR / ".plugin_manager" / "tools" / "support.ini"
    )
    for _directory in server_directories:
        _path = Path(_directory)
        for _check_directory in _path.dirs():
            if not any(
                _check_directory.joinpath(_check_file).is_file()
                for _check_file in _check_files
            ):
                continue
            for _game, _values in _support.items():
                _game_dir = _check_directory / _values["folder"]
                if not _game_dir.is_dir():
                    continue
                if _game in games:
                    continue
                games[_game] = {
                    "directory": _game_dir,
                    "branch": _values["branch"],
                }
    return games

supported_games = _get_supported_games()
