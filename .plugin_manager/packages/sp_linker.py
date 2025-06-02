# ../sp_linker.py

"""Links Source.Python's repository to games/servers."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
from contextlib import suppress
from warnings import warn

# Site-package
from configobj import ConfigObj
from path import Path

# Package
from common.constants import (
    PLATFORM,
    START_DIR,
    config,
)
from common.functions import (
    clear_screen,
    copy_over_file,
    link_directory,
    link_file,
)

# ==============================================================================
# >> GLOBAL VARIABLES
# ==============================================================================
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
source_python_addons_directories = {
    x.stem for x in SOURCE_PYTHON_DIR.joinpath(
        "addons",
        "source-python",
    ).dirs() if x.stem != "bin"
}


# ==============================================================================
# >> CLASSES
# ==============================================================================
class SPLinker:
    def __init__(self, game_name):
        if game_name not in supported_games:
            msg = f"{game_name} is not a supported game"
            raise ValueError(msg)
        self.game_name = game_name

    def link_game(self):
        print(f"Linking Source.Python to {self.game_name}.\n")
        path = supported_games[self.game_name]["directory"]
        branch = supported_games[self.game_name]["branch"]
        for dir_name in source_python_directories:
            directory = path / dir_name
            if not directory.is_dir():
                directory.makedirs()

            sp_dir = directory / "source-python"
            if sp_dir.is_dir():
                print(
                    f"Cannot link ../{dir_name}/source-python/ directory."
                    f"  Directory already exists.\n",
                )
                continue

            link_directory(
                src=SOURCE_PYTHON_DIR / dir_name / "source-python",
                dest=sp_dir,
            )
            print(f"Successfully linked ../{dir_name}/source-python/\n")

        server_addons = path / "addons" / "source-python"
        if not server_addons.is_dir():
            server_addons.makedirs()

        for dir_name in source_python_addons_directories:
            directory = server_addons / dir_name
            if directory.is_dir():
                print(
                    f"Cannot link ../addons/source-python/{dir_name}/ "
                    f"directory.  Directory already exists.\n",
                )
                continue

            link_directory(
                src=SOURCE_PYTHON_ADDONS_DIR / dir_name,
                dest=directory,
            )
            print(f"Successfully linked ../addons/source-python/{dir_name}/\n")

        bin_dir = server_addons / "bin"
        if not bin_dir.is_dir():
            SOURCE_PYTHON_ADDONS_DIR.joinpath("bin").copytree(bin_dir)

        vdf = path / "addons" / "source-python.vdf"
        if not vdf.is_file():
            SOURCE_PYTHON_DIR.joinpath("addons", "source-python.vdf").copy(vdf)

        build_dir = SOURCE_PYTHON_BUILDS_DIR / branch
        if PLATFORM == "windows":
            build_dir = build_dir / "Release"

        if not build_dir.is_dir():
            warn(
                f'Build "{branch}" does not exist. Please create the build.',
            )
            return

        copy_over_file(
            src=build_dir / SOURCE_BINARY,
            dest=path / "addons" / SOURCE_BINARY,
        )
        copy_over_file(
            src=build_dir / CORE_BINARY,
            dest=path / "addons" / "source-python" / "bin" / CORE_BINARY,
        )


# ==============================================================================
# >> HELPER FUNCTIONS
# ==============================================================================
def _get_game():
    """Return a game to do something with."""
    clear_screen()

    # Are there any games?
    if not supported_games:
        print("There are no games to link.")
        return None

    # Gather the list of games
    message = "Which game/server would you like to link?\n\n"
    for number, game in enumerate(supported_games, start=1):
        message += f"\t({number}) {game}\n"

    # Add ALL to the list
    message += f"\t({len(supported_games) + 1}) ALL\n\n"

    # Get the game to link to
    while True:
        value = input(message).strip()
        if value in [*supported_games, "ALL"]:
            return value

        with suppress(ValueError):
            value = int(value)
            if value <= len(supported_games):
                return list(supported_games)[value - 1]

            if value == len(supported_games) + 1:
                return "ALL"


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
                    warn(
                        f"{_game} already assigned to {games[_game]}."
                        f" New path found: {_game_dir}",
                    )
                    continue
                games[_game] = {
                    "directory": _game_dir,
                    "branch": _values["branch"],
                }
    return games

supported_games = _get_supported_games()


# ==============================================================================
# >> MAIN FUNCTION
# ==============================================================================
def run():
    # Get the game to link
    game_name = _get_game()
    if game_name is not None:
        clear_screen()
        if game_name == "ALL":
            for game_name in supported_games:
                SPLinker(game_name).link_game()

        else:
            SPLinker(game_name).link_game()


if __name__ == "__main__":
    run()
