# ../plugin_releaser.py

"""Creates a release for a plugin with its current version number."""
# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import tkinter as tk
from zipfile import ZIP_DEFLATED, ZipFile

# Package
from common.constants import (
    PLUGIN_LIST,
    RELEASE_DIR,
    START_DIR,
    config,
)
from common.interface import BaseInterface

# Site-package
from configobj import ConfigObj
from git import Repo


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_version_updates = [
    "MAJOR",
    "MINOR",
    "PATCH",
    None,
]

# Store plugin specific directories with their respective allowed file types
_readable_data = [
    "ini",
    "json",
    "vdf",
    "xml",
]
ALLOWED_FILETYPES = {
    config["PLUGIN_BASE_PATH"]: [*_readable_data, "md", "py"],
    config["DATA_BASE_PATH"]: [*_readable_data, "md", "txt"],
    config["CONFIG_BASE_PATH"]: [*_readable_data, "cfg", "md", "txt"],
    config["LOGS_BASE_PATH"]: ["md", "txt"],
    config["SOUND_BASE_PATH"]: ["md", "mp3", "wav"],
    config["EVENTS_BASE_PATH"]: ["md", "txt"],
    config["TRANSLATIONS_BASE_PATH"]: ["md", "ini"],
    "materials/": ["vmt", "vtf"],
    "models/": ["mdl", "phy", "vtx", "vvd"],
}

# Store directories with files that fit allowed_filetypes
#   with names that should not be included
EXCEPTION_FILETYPES = {
    config["TRANSLATIONS_BASE_PATH"]: ["_server.ini"],
}


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Plugin Releaser"
    plugin_name = None
    update_type = None
    new_version = None

    def run(self):
        self.plugin_name = None
        self.window.title(self.name)
        self.clear_grid()
        self.create_grid(data=PLUGIN_LIST)
        self.add_back_button(self.on_back_to_main)

    def get_info_for_plugin(self):
        if self.plugin_name is None:
            return None

        return ConfigObj(
            START_DIR.joinpath(
                self.plugin_name,
                config["PLUGIN_BASE_PATH"],
                self.plugin_name,
                "info.ini",
            )
        )

    def on_click(self, option):
        self.clear_grid()
        self.plugin_name = option
        self.new_version = None
        self.update_type = None
        repo = Repo(START_DIR / self.plugin_name)
        if (
            bool(repo.index.diff('HEAD')) or
            bool(repo.index.diff(None)) or
            bool(repo.untracked_files)
        ):
            label = tk.Label(
                self.window,
                text=(
                    f"{option} has uncommitted changes, cannot create release"
                ),
                font=("times", 12, "bold"),
            )
            label.pack()

        else:
            current_version = self.get_info_for_plugin()["version"]
            label_frame = tk.Frame(self.window)
            label_frame.pack(fill="x", padx=10, pady=(10, 0))
            label = tk.Label(
                label_frame,
                text=f"{option} Current Version: {current_version}",
                font=("times", 12, "bold"),
            )
            label.pack()
            button_frame = tk.Frame(self.window)
            button_frame.pack(pady=10)
            for i, label in enumerate(_version_updates):
                button = tk.Button(
                    button_frame,
                    text=str(label),
                    command=lambda l=label: self.on_update_type_click(l),
                    width=15,
                )
                button.pack(pady=2)
        self.add_back_button(self.run)

    def on_update_type_click(self, option):
        self.clear_grid()
        self.update_type = option
        current_version = self.get_info_for_plugin()["version"]
        version_list = list(
            map(
                int,
                current_version.split("."),
            )
        )
        label_frame = tk.Frame(self.window)
        label_frame.pack(fill="x", padx=10, pady=(10, 0))
        index = _version_updates.index(option)
        if index >= len(version_list):
            self.create_release()
            return

        version_list[index] += 1
        version_list[index + 1:] = [0] * (len(version_list) - (index + 1))
        self.new_version = ".".join(map(str, version_list))
        label = tk.Label(
            label_frame,
            text=(
                f"{self.plugin_name} Current Version: {current_version}\n"
                f"Update to version '{self.new_version}'?"
            ),
            font=("times", 12, "bold"),
        )
        label.pack()
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        for label, value in (("Yes", True), ("No", False)):
            button = tk.Button(
                button_frame,
                text=str(label),
                command=lambda v=value: self.on_acknowledge_update(v),
                width=15,
            )
            button.pack(pady=2)
        self.add_back_button(lambda p=self.plugin_name: self.on_click(p))

    def on_acknowledge_update(self, option):
        if not option:
            self.on_click(self.plugin_name)
            return

        self.create_release()

    def create_release(self):
        self.clear_grid()
        commands = []
        console = self.get_console()
        repo = Repo(START_DIR / self.plugin_name)
        if self.new_version is not None:
            version = self.new_version
            self.update_version(repo)
        else:
            version = self.get_info_for_plugin()["version"]
        self.execute_console_commands(
            console=console,
            commands=commands,
        )
        self.add_back_button(self.run)

        save_path = RELEASE_DIR / self.plugin_name
        if not save_path.is_dir():
            save_path.makedirs()

        zip_path = save_path / f"{self.plugin_name} - v{version}.zip"
        if zip_path.is_file():
            print("Release already exists for current version.")
            return

        repo_files = repo.git.ls_files().splitlines()

        # Create the zip file
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zip_file:
            for repo_file in repo_files:
                if self.validate_file_by_base_path(repo_file):
                    self.add_file(
                        relative_file_path=repo_file,
                        zip_file=zip_file,
                        plugin_path=START_DIR / self.plugin_name,
                    )

        print(f"Saved release to {zip_path}")

    def update_version(self, repo):
        print(f"Updating {self.plugin_name} to version '{self.new_version}'")
        info = self.get_info_for_plugin()
        info["version"] = self.new_version
        info.write()
        repo.git.add(
            "--verbose",
            f"{config['PLUGIN_BASE_PATH']}/{self.plugin_name}/info.ini",
        )
        print(
            repo.git.commit(
                "-m",
                f"{self.update_type} version update ({self.new_version})"
            )
        )
        results = repo.remotes.origin.push()
        for info in results:
            print(info.summary)

    @staticmethod
    def validate_file_by_base_path(file):
        for allowed_path in ALLOWED_FILETYPES:
            if file.startswith(allowed_path):
                if (
                    allowed_path in EXCEPTION_FILETYPES and
                    file.endswith(*EXCEPTION_FILETYPES[allowed_path])
                ):
                    return False
                return True
        return False

    @staticmethod
    def add_file(relative_file_path, zip_file, plugin_path):
        """Add the given file and all parent directories to the zip."""
        full_file_path = plugin_path / relative_file_path
        zip_file.write(full_file_path, relative_file_path)
        directory = full_file_path.parent

        # Get all parent directories to add to the zip
        while directory != plugin_path:

            # Is the current directory not yet included in the zip?
            current = directory.replace(
                plugin_path,
                "",
            )[1:].replace("\\", "/") + "/"
            if current not in zip_file.namelist():
                zip_file.write(directory, current)

            directory = directory.parent
