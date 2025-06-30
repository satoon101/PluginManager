# ../plugin_creator.py

"""Creates a plugin with its base directories and files."""
# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import re
import tkinter as tk
from contextlib import suppress

# Site-package
from git import Repo
from github import Github
from jinja2 import Template

# Package
from common.constants import (
    CONDITIONAL_PYTHON_FILES_DIR,
    PLUGIN_PRIMARY_FILES_DIR,
    PLUGIN_REPO_ROOT_FILES_DIR,
    START_DIR,
    PLUGIN_LIST,
    config,
)
from common.interface import BaseInterface

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CHECKBOX_PER_ROW = 2
given_conditional_paths = config["CONDITIONAL_FILE_OR_DIRECTORY"]
allowed_conditional_paths = {
    "config": {
        "path": config["CONFIG_BASE_PATH"],
        "extension": "cfg",
    },
    "data": {
        "path": config["DATA_BASE_PATH"],
        "extension": "json",
    },
    "docs": {
        "path": config["DOCS_BASE_PATH"],
        "extension": "rst",
    },
    "events": {
        "path": config["EVENTS_BASE_PATH"],
        "extension": "res",
    },
    "logs": {
        "path": config["LOGS_BASE_PATH"],
        "extension": "log",
    },
    "sound": {
        "path": config["SOUND_BASE_PATH"],
        "extension": "md",
    },
    "translations": {
        "path": config["TRANSLATIONS_BASE_PATH"],
        "extension": "ini",
    },
}
found_conditional_files = [
    str(item.stem) for item in CONDITIONAL_PYTHON_FILES_DIR.files()
    if item.name != "delete.me"
]
given_conditional_files = config["CONDITIONAL_PYTHON_FILES"]


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Plugin Creator"
    checkbox_var = None
    entry_box = None
    plugin_name = None
    conditional_python_files = {}
    conditional_file_or_directory = {}
    conditional_paths = {}

    def run(self):
        self.window.title(self.name)
        self.clear_grid()
        message = ""
        diff = set(given_conditional_paths).difference(
            allowed_conditional_paths,
        )
        if diff:
            message += (
                f"Invalid conditional files or directories in configuration:"
                f"\n\t{', '.join(sorted(diff))}\n\n"
            )
        diff = set(found_conditional_files).difference(given_conditional_files)
        if diff:
            message += (
                f"Conditional files found in directory, but not in "
                f"configuration:\n\t{', '.join(sorted(diff))}\n\n"
            )
        diff = set(given_conditional_files).difference(found_conditional_files)
        if diff:
            message += (
                f"Conditional files found in configuration, but not in "
                f"directory:\n\t{', '.join(sorted(diff))}"
            )
        if message:
            label = tk.Label(
                self.window,
                text=message,
                font=("times", 20, "bold"),
            )
            label.pack()
            return
        self.checkbox_var = None
        self.entry_box = None
        self.plugin_name = None
        self.conditional_python_files.clear()
        self.conditional_file_or_directory.clear()
        self.conditional_paths.clear()
        label = tk.Label(
            self.window,
            text="Enter the name of the plugin:",
            font=("times", 20, "bold"),
        )
        label.pack(pady=(0, 10))
        label2 = tk.Label(
            self.window,
            text=(
                "First character must be a lowercase letter.\n"
                "Characters must be lowercase, numbers, and underscores only."
            ),
            font=("times", 12),
        )
        label2.pack(pady=(0, 10))
        vcmd = (self.window.register(self.validate_input), "%P")
        entry = tk.Entry(
            self.window,
            width=30,
            validate="key",
            validatecommand=vcmd,
        )
        entry.pack(pady=(0, 10))
        submit_btn = tk.Button(
            self.window,
            text="Submit",
            command=lambda e=entry: self.on_submit_plugin_name(e),
        )
        submit_btn.pack()
        self.add_back_button(self.on_back_to_main)

    @staticmethod
    def validate_input(value):
        pattern = r"^[a-z][a-z0-9_]*$"
        return re.fullmatch(pattern, value) is not None or value == ""

    def on_submit(self):
        repo_name = self.entry_box.get()
        self.clear_grid()
        self.get_console()
        print(f"Creating plugin {self.plugin_name}")
        base_path = START_DIR / self.plugin_name
        self.create_root_files(base_path)
        plugin_path = base_path / config["PLUGIN_BASE_PATH"] /self.plugin_name
        self.create_primary_files(plugin_path)
        self.create_conditional_python_files(base_path, plugin_path)
        self.create_conditional_file_or_directory(base_path)
        self.create_conditional_paths(base_path)
        if self.checkbox_var.get():
            self.create_github_repository(base_path, repo_name)

        self.add_back_button(self.run)

    def on_submit_plugin_name(self, entry):
        self.plugin_name = entry.get()
        prefix = config["PREFIX"]
        if prefix and not self.plugin_name.startswith(prefix):
            self.plugin_name = f"{prefix}_{self.plugin_name}"

        self.clear_grid()
        if self.plugin_name in PLUGIN_LIST:
            label = tk.Label(
                self.window,
                text=f"Plugin name already exists: {self.plugin_name}",
                font=("times", 20, "bold"),
            )
            label.pack()
            self.add_back_button(self.run)
            return
        self.checkbox_var = tk.BooleanVar()
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill="x", padx=10, pady=5)
        checkbox = tk.Checkbutton(
            top_frame,
            text="Create Github repository (input repository name)",
            font=("times", 14, "bold"),
            variable=self.checkbox_var,
            command=self.toggle_entry,
        )
        checkbox.pack(pady=(10, 5))
        self.entry_box = tk.Entry(
            top_frame,
            font=("consolas", 12),
            width=30,
        )
        repo_prefix = config["REPO_PREFIX"]
        prefix = config["PREFIX"]
        plugin_name = self.plugin_name
        if plugin_name.startswith(prefix):
            plugin_name = plugin_name[len(prefix):]
        repo_name = "".join(plugin_name.title().split("_"))
        self.entry_box.insert(0, f"{repo_prefix}{repo_name}")
        self.entry_box.configure(state="disabled")
        self.entry_box.pack(pady=(0, 10))

        data = self.get_conditional_python_file_data()
        frame = self.create_section(
            data=data,
            text="Create conditional file or directory for the following?",
            mapping=self.conditional_python_files,
            checkbox_per_row=4,
            skip_rows=True,
            command=self.update_children,
        )
        children = {
            child.cget("text"): child
            for child in frame.winfo_children()
        }
        for i, value in enumerate(data):
            key = value.replace(".py", "")
            values = config["CONDITIONAL_PYTHON_FILES"][key]
            always = values.get("always_create_translations_file")
            path = values.get("translations_file_path")
            if path is None:
                continue

            if values["always_create_file"] == "true":
                widget = children[value]
                widget.configure(state="disabled")
                self.conditional_python_files[value].set(True)

            translation_key = f"{value}-translation"
            if always == "true":
                self.conditional_python_files[translation_key] = True
            if always == "false":
                row = (i // 4) * 2 + 1
                col = i % 4
                variable = self.conditional_python_files[
                    translation_key
                ] = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    frame,
                    text=f"{key} translations file",
                    variable=variable,
                )
                if not self.conditional_python_files[value].get():
                    checkbox.configure(state="disabled")

                checkbox.grid(
                    row=row,
                    column=col,
                    padx=10,
                    pady=10,
                    sticky="ew",
                )
                widget_key = f"{translation_key}-widget"
                self.conditional_python_files[widget_key] = checkbox

        data = self.get_conditional_file_or_directory_data()
        self.create_section(
            data=data,
            text="Create conditional file or directory for the following?",
            mapping=self.conditional_file_or_directory,
        )

        data = list(self.get_conditional_paths_data())
        self.create_section(
            data=data,
            text="Create the following conditional paths?",
            mapping=self.conditional_paths,
            checkbox_per_row=1,
        )
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        submit_btn = tk.Button(
            bottom_frame,
            text="Submit",
            command=self.on_submit,
        )
        submit_btn.pack()

        self.add_back_button(self.run)

    def update_children(self):
        for item in config["CONDITIONAL_PYTHON_FILES"]:
            key = f"{item}.py"
            translation_key = f"{key}-translation"
            if translation_key not in self.conditional_python_files:
                continue
            child = self.conditional_python_files[translation_key]
            if isinstance(child, bool):
                continue
            parent = self.conditional_python_files[key]
            state = "normal" if parent.get() else "disabled"
            widget = self.conditional_python_files[f"{translation_key}-widget"]
            widget.configure(state=state)
            if state == "disabled":
                child.set(False)

    def toggle_entry(self):
        self.entry_box.configure(
            state="normal" if self.checkbox_var.get() else "disabled",
        )

    def create_checkbox_grid(
        self,
        data,
        mapping,
        container=None,
        checkbox_per_row=CHECKBOX_PER_ROW,
        skip_rows=False,
        command=None,
    ):
        container = container or self.window
        for i, label in enumerate(data):
            row = i // checkbox_per_row
            if skip_rows:
                row *= 2
            col = i % checkbox_per_row
            mapping[label] = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                container,
                text=label,
                variable=mapping[label],
                command=command,
            )
            checkbox.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        for i in range(checkbox_per_row):
            container.grid_columnconfigure(i, weight=1)

        for i in range((len(data) + checkbox_per_row - 1) // checkbox_per_row):
            container.grid_rowconfigure(i, weight=1)

    def create_section(
        self,
        data,
        text,
        mapping,
        checkbox_per_row=CHECKBOX_PER_ROW,
        skip_rows=False,
        command=None,
    ):
        if not data:
            return None

        frame1 = tk.Frame(self.window)
        frame1.pack(fill="x", padx=10, pady=5)
        label = tk.Label(
            frame1,
            text=text,
            font=("times", 14, "bold"),
        )
        label.pack()
        frame2 = tk.Frame(self.window)
        frame2.pack(fill="x", padx=10, pady=5)
        self.create_checkbox_grid(
            data=data,
            mapping=mapping,
            container=frame2,
            checkbox_per_row=checkbox_per_row,
            skip_rows=skip_rows,
            command=command,
        )
        return frame2

    @staticmethod
    def get_conditional_python_file_data():
        return [
            f"{item}.py"
            for item, values in config["CONDITIONAL_PYTHON_FILES"].items()
            if values["always_create_file"] != "true" or (
                values["always_create_file"] == "true" and
                values["always_create_translations_file"] == "false" and
                values["translations_file_path"]
            )
        ]

    def get_conditional_file_or_directory_data(self):
        data = []
        for item, value in config["CONDITIONAL_FILE_OR_DIRECTORY"].items():
            values = allowed_conditional_paths[item]
            base = f"{values['path']}/{self.plugin_name}"
            if value in ("dir", "both"):
                data.append(f"{base}/")
            if value in ("file", "both"):
                data.append(f"{base}.{values['extension']}")

        return sorted(data)

    def get_conditional_paths_data(self):
        for value in config["CONDITIONAL_PATHS"].values():
            yield value.format(plugin_name=self.plugin_name)

    @staticmethod
    def create_root_files(base_path):
        base_path.makedirs()
        for file in PLUGIN_REPO_ROOT_FILES_DIR.files():
            if file.name == "delete.me":
                continue
            file.copy(
                base_path / file.name,
            )

    def create_primary_files(self, plugin_path):
        plugin_path.makedirs()
        for file in PLUGIN_PRIMARY_FILES_DIR.files():
            if file.name == "delete.me":
                continue
            new_file = plugin_path / file.name
            self._copy_and_format_file(
                file=file,
                new_file=new_file,
            )

    def create_conditional_python_files(self, base_path, plugin_path):
        for item, values in config["CONDITIONAL_PYTHON_FILES"].items():
            key = f"{item}.py"
            if not self.conditional_python_files[key].get():
                continue
            file = CONDITIONAL_PYTHON_FILES_DIR / key
            new_file = plugin_path / file.name
            self._copy_and_format_file(
                file=file,
                new_file=new_file,
            )
            translations_key = f"{key}-translation"
            create_file = self.conditional_python_files.get(translations_key)
            if create_file is None:
                continue

            with suppress(AttributeError):
                create_file = create_file.get()

            if not create_file:
                continue

            path = values["translations_file_path"].format(
                plugin_name=self.plugin_name,
            )
            path = base_path / config["TRANSLATIONS_BASE_PATH"] / path
            self._create_directory_and_file(path)

    def create_conditional_file_or_directory(self, base_path):
        for path, value in self.conditional_file_or_directory.items():
            if value.get():
                self._create_directory_and_file(base_path / path)

    def create_conditional_paths(self, base_path):
        for path, value in self.conditional_paths.items():
            if value.get():
                self._create_directory_and_file(base_path / path)

    @staticmethod
    def create_github_repository(base_path, repo_name):
        repo = Repo.init(base_path, initial_branch="master")
        for file in base_path.files():
            repo.index.add(file.name)
        repo.index.commit("Initial commit")
        access_token = config["ACCESS_TOKEN"]
        if not access_token:
            return

        github = Github(access_token)
        user = github.get_user()
        remote_url = user.create_repo(
            repo_name,
            private=False,
            auto_init=False,
        ).ssh_url
        repo.create_remote("origin", url=remote_url)
        repo.git.push("--set-upstream", "origin", "master")

    def _copy_and_format_file(self, file, new_file):
        if file.stem == "plugin":
            new_file = new_file.with_stem(self.plugin_name)
        with file.open() as open_file:
            file_contents = Template(open_file.read())

        file_contents = file_contents.render(
            plugin_name=self.plugin_name,
            plugin_prefix="".join(
                [i[0] for i in self.plugin_name.split("_")]
            ) + "_",
            author=config["AUTHOR"],
        )
        if not file_contents.endswith('\n'):
            file_contents += '\n'
        with new_file.open("w") as open_file:
            open_file.write(file_contents)

    @staticmethod
    def _create_directory_and_file(path):
        directory = path
        if path.suffix:
            directory = path.parent
        if not directory.is_dir():
            directory.makedirs()
        if path.suffix:
            path.touch()
