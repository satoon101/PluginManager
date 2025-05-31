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
    CORE_BINARY,
    PLATFORM,
    SOURCE_BINARY,
    SOURCE_PYTHON_DIR,
    START_DIR,
    config,
)
from common.functions import clear_screen, link_directory, link_file


# ==============================================================================
# >> MAIN FUNCTION
# ==============================================================================
def get_game():
    """Return a game to do something with."""
    # Clear the screen
    clear_screen()

    # Are there any games?
    if not supported_games:
        print("There are no games to link.")
        return None

    # Get the question to ask
    message = "Which game/server would you like to link?\n\n"

    # Loop through each game
    for number, game in enumerate(supported_games, 1):

        # Add the current game
        message += f"\t({number}) {game}\n"

    # Add ALL to the list
    message += f"\t({len(supported_games) + 1}) ALL\n"

    # Ask which game to do something with
    value = input(f"{message}\n").strip()

    # Was a game name given?
    if value in [*supported_games, "ALL"]:

        # Return the value
        return value

    # Was an integer given?
    with suppress(ValueError):

        # Typecast the value
        value = int(value)

        # Was the value a valid server choice?
        if value <= len(supported_games):

            # Return the game by index
            return list(supported_games)[value - 1]

        # Was ALL's choice given?
        if value == len(supported_games) + 1:

            # Return ALL
            return "ALL"

    # If no valid choice was given, try again
    return get_game()


def link_game(game_name):
    """Link Source.Python's repository to the given game/server."""
    # Was an invalid game name given?
    if game_name not in supported_games:
        print(f'Invalid game name "{game_name}".')
        return

    # Print a message about the linking
    print(f"Linking Source.Python to {game_name}.\n")

    # Link Source.Python to the game
    link_source_python(game_name)


def link_source_python(game_name):
    """Link Source.Python's repository to the given game/server."""
    # Get the path to the game/server
    path = supported_games[game_name]["directory"]

    # Loop through each directory to link
    for dir_name in source_python_directories:

        # Get the directory path
        directory = path / dir_name

        # Create the directory if it doesn't exist
        if not directory.is_dir():
            directory.makedirs()

        # Get the source-python path
        sp_dir = directory / "source-python"

        # Does the source-python sub-directory already exist?
        if sp_dir.is_dir():
            print(
                f"Cannot link ../{dir_name}/source-python/ directory."
                f"  Directory already exists.\n",
            )
            continue

        # Link the directory
        link_directory(
            SOURCE_PYTHON_DIR / dir_name / "source-python", sp_dir,
        )
        print(f"Successfully linked ../{dir_name}/source-python/\n")

    # Get the server's addons directory
    server_addons = path / "addons" / "source-python"

    # Create the addons directory if it doesn't exist
    if not server_addons.is_dir():
        server_addons.makedirs()

    # Loop through each directory to link
    for dir_name in source_python_addons_directories:

        # Get the directory path
        directory = server_addons / dir_name

        # Does the directory already exist on the server?
        if directory.is_dir():
            print(
                f"Cannot link ../addons/source-python/{dir_name}/ "
                f"directory.  Directory already exists.\n",
            )
            continue

        # Link the directory
        link_directory(SOURCE_PYTHON_ADDONS_DIR / dir_name, directory)
        print(f"Successfully linked ../addons/source-python/{dir_name}/\n")

    # Get the bin directory
    bin_dir = server_addons / "bin"

    # Copy the bin directory if it doesn't exist
    if not bin_dir.is_dir():
        SOURCE_PYTHON_ADDONS_DIR.joinpath("bin").copytree(bin_dir)

    # Get the .vdf's path
    vdf = path / "addons" / "source-python.vdf"

    # Copy the .vdf if it needs copied
    if not vdf.is_file():
        SOURCE_PYTHON_DIR.joinpath("addons", "source-python.vdf").copy(vdf)

    # Get the build directory for the game/server's branch
    build_dir = SOURCE_PYTHON_BUILDS_DIR / supported_games[game_name]["branch"]

    # Add 'Release' to the directory if Windows
    if PLATFORM == "windows":
        build_dir = build_dir / "Release"

    # If the build directory doesn't exist, create the build
    if not build_dir.is_dir():
        warn(
            f'Build "{supported_games[game_name]["branch"]}" does not exist. '
            f'Please create the build.',
        )
        return

    # Link the files
    link_file(build_dir / SOURCE_BINARY, path / "addons" / SOURCE_BINARY)
    link_file(
        build_dir / CORE_BINARY,
        path / "addons" / "source-python" / "bin" / CORE_BINARY,
    )


# ==============================================================================
# >> CALL MAIN FUNCTION
# ==============================================================================
if __name__ == "__main__":

    # Get the game to link
    _game_name = get_game()

    # Was a valid game chosen?
    if _game_name is not None:

        # Clear the screen
        clear_screen()

        # Was ALL selected?
        if _game_name == "ALL":

            # Loop through each game
            for _game_name in supported_games:

                # Link the game
                link_game(_game_name)

        # Otherwise
        else:

            # Link the game
            link_game(_game_name)


# Get Source.Python's addons directory
SOURCE_PYTHON_ADDONS_DIR = SOURCE_PYTHON_DIR / "addons" / "source-python"

# Get Source.Python's build directory
SOURCE_PYTHON_BUILDS_DIR = SOURCE_PYTHON_DIR.joinpath(
    "src",
    "Builds",
    "Windows" if PLATFORM == "windows" else "Linux",
)

# Get the directories to link
source_python_directories = {
    x.stem for x in SOURCE_PYTHON_DIR.dirs()
    if x.stem not in ("addons", "src", ".git")
}

# Get the addons directories to link
source_python_addons_directories = {
    x.stem for x in SOURCE_PYTHON_DIR.joinpath(
        "addons",
        "source-python",
    ).dirs() if x.stem != "bin"
}

_support = ConfigObj(START_DIR / ".plugin_manager" / "tools" / "support.ini")

supported_games = {}

_check_files = ["srcds.exe", "srcds_run", "srcds_linux"]

for _directory in config["SERVER_DIRECTORIES"].split(";"):
    _path = Path(_directory)
    for _check_directory in _path.dirs():
        if not any(
            _check_directory.joinpath(_check_file).is_file()
            for _check_file in _check_files
        ):
            continue
        for _game in _support["servers"]:
            _game_dir = _check_directory / _support["servers"][_game]["folder"]
            if not _game_dir.is_dir():
                continue
            if _game in supported_games:
                warn(
                    f"{_game} already assigned to {supported_games[_game]}.  "
                    f"New path found: {_game_dir}",
                )
                continue
            supported_games[_game] = {
                "directory": _game_dir,
                "branch": _support["servers"][_game]["branch"],
            }
