# ../plugin_creator.py

"""Creates a plugin with its base directories and files."""
# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
from contextlib import suppress
from functools import cached_property
from warnings import warn

# Site-package
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
from common.functions import clear_screen

# ==============================================================================
# >> GLOBAL VARIABLES
# ==============================================================================
_boolean_values = {
    "1": True,
    "y": True,
    "yes": True,
    "2": False,
    "n": False,
    "no": False,
}

_directory_or_file = {
    "1": "file",
    "2": "dir",
    "3": None,
}

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
diff = set(given_conditional_paths).difference(allowed_conditional_paths)
if diff:
    _msg = f"Invalid conditional paths: {', '.join(sorted(diff))}"
    raise ValueError(_msg)

found_conditional_files = [
    str(item.stem) for item in CONDITIONAL_PYTHON_FILES_DIR.files()
    if item.name != "delete.me"
]
given_conditional_files = config["CONDITIONAL_PYTHON_FILES"]
diff = set(found_conditional_files).difference(given_conditional_files)
if diff:
    _msg = (
        f"Conditional files found in directory, but not in configuration:"
        f" {', '.join(sorted(diff))}"
    )
    raise ValueError(_msg)

diff = set(given_conditional_files).difference(found_conditional_files)
if diff:
    _msg = (
        f"Conditional files found in configuration, but not in directory:"
        f" {', '.join(sorted(diff))}"
    )
    raise ValueError(_msg)


# ==============================================================================
# >> CLASSES
# ==============================================================================
class PluginCreater:
    def __init__(self, plugin_name, options):
        self.plugin_name = plugin_name
        if config["PREFIX"]:
            self.plugin_name = f"{config['PREFIX']}_{self.plugin_name}"
        self.options = options
        self.validate_plugin_name()

    @cached_property
    def plugin_base_path(self):
        return START_DIR / self.plugin_name

    @cached_property
    def plugin_path(self):
        return self.plugin_base_path.joinpath(
            config["PLUGIN_BASE_PATH"],
            self.plugin_name,
        )

    @cached_property
    def plugin_prefix(self):
        return "".join([i[0] for i in self.plugin_name.split("_")]) + "_"

    def validate_plugin_name(self):
        # Was no plugin name provided?
        if self.plugin_name is None:
            msg = "No plugin name provided."
            raise ValueError(msg)

        # Is the given plugin name valid?
        if not self.plugin_name.replace("_", "").isalnum():
            msg = (
                f"Invalid plugin name: {self.plugin_name}\nPlugin name must "
                f"only contain alpha-numeric values and underscores."
            )
            raise ValueError(msg)

        # Has the plugin already been created?
        if self.plugin_base_path.is_dir():
            msg = f'Plugin "{self.plugin_name} already exists.'
            raise ValueError(msg)

    def create_plugin(self):
        # Create the plugin's directory
        self.plugin_path.makedirs()
        self.create_primary_files()
        self.copy_extra_python_files()
        self.create_extra_directories_and_files()
        self.create_conditional_paths()

    def create_primary_files(self):
        """Copy repo primary files to the repository."""
        for file in PLUGIN_PRIMARY_FILES_DIR.files():
            if file.name == "delete.me":
                continue
            self._copy_and_format_file(
                file=file,
            )

        # Copy repo base files
        for file in PLUGIN_REPO_ROOT_FILES_DIR.files():
            if file.name == "delete.me":
                continue
            file.copy(
                self.plugin_base_path / file.name,
            )

    def copy_extra_python_files(self):
        """Copy any of the extra base plugin files."""
        for key, value in config["CONDITIONAL_PYTHON_FILES"].items():
            key = f"{key}.py"
            if not self.options["python"].get(key):
                continue
            self._copy_and_format_file(
                file=CONDITIONAL_PYTHON_FILES_DIR / key,
            )
            if not self.options["python"].get(f"{key}_translations"):
                continue
            self._create_file_or_directory(
                self.plugin_base_path,
                config["TRANSLATIONS_BASE_PATH"],
                self.options["python"].get(f"{key}_translation_path"),
                filename=f"{self.plugin_name}.ini",
            )

    def create_extra_directories_and_files(self):
        """Create the extra files/directories based on the configuration."""
        for key, values in config["CONDITIONAL_FILE_OR_DIRECTORY"].items():
            value = self.options["file_or_directory"].get(key)
            if not value:
                continue
            path = allowed_conditional_paths[key]["path"]
            extension = allowed_conditional_paths[key]["extension"]
            if value == "file":
                self._create_file_or_directory(
                    self.plugin_base_path,
                    path,
                    filename=f"{self.plugin_name}.{extension}",
                )
            elif value == "dir":
                self._create_file_or_directory(
                    self.plugin_base_path,
                    path,
                    self.plugin_name,
                )
            else:
                warn(
                    message=f"Invalid value given for option '{key}': {value}",
                    stacklevel=2,
                )

    def create_conditional_paths(self):
        for key, path in config["CONDITIONAL_PATHS"].items():
            value = self.options["paths"].get(key)
            if not value:
                continue
            path = dir_path = self.plugin_base_path.joinpath(
                path.format(plugin_name=self.plugin_name),
            )
            if path.suffix:
                dir_path = path.parent
            if not dir_path.is_dir():
                dir_path.makedirs()
            if path.suffix:
                path.touch()

    def _copy_and_format_file(self, file):
        new_file = self.plugin_path / file.name
        if file.stem == "plugin":
            new_file = new_file.with_stem(self.plugin_name)
        with file.open() as open_file:
            file_contents = Template(open_file.read())

        file_contents = file_contents.render(
            plugin_name=self.plugin_name,
            plugin_prefix=self.plugin_prefix,
            author=config["AUTHOR"],
        )
        if not file_contents.endswith('\n'):
            file_contents += '\n'
        with new_file.open("w") as open_file:
            open_file.write(file_contents)

    @staticmethod
    def _create_file_or_directory(base_path, *args, filename=None):
        """Create the directory using the given arguments."""
        current_path = base_path.joinpath(*args)
        current_path.makedirs()
        if filename is not None:
            current_path.joinpath(filename).touch()


# ==============================================================================
# >> HELPER FUNCTIONS
# ==============================================================================
def _get_plugin_name():
    """Return a new plugin name."""
    clear_screen()

    while True:
        name = input(
            "What is the name of the plugin that should be created?\n\n"
        )
        try:
            # Is the plugin name invalid?
            assert name.replace("_", "").isalnum()
        except AssertionError:
            clear_screen()
            print(
                f'Invalid characters used in plugin name "{name}".\n'
                f'Only alpha-numeric and underscores allowed.',
            )
        else:
            check_name = f"{config['PREFIX']}_{name}"
            if check_name in PLUGIN_LIST:
                clear_screen()
                print(f'Plugin name "{name}" already exists.')
            else:
                return name


def _get_extra_file(name):
    """."""
    while True:
        clear_screen()
        value = input(
            f"Do you want a copy of the {name} file for your plugin?\n\n"
            f"\t(1) Yes\n\t(2) No\n\n",
        )
        with suppress(KeyError):
            return _boolean_values[value]


def _get_translation_file(name, always_create):
    """."""
    if always_create:
        return always_create

    while True:
        clear_screen()
        value = input(
            f"Do you want to create a translation file for {name} file?\n\n"
            f"\t(1) Yes\n\t(2) No\n\n"
        )
        with suppress(KeyError):
            return _boolean_values[value]


def _get_directory_or_file(name, item):
    """Return whether to create the given directory or file."""
    if item in ("file", "dir"):
        text = (
            f"Do you want to include a {name} {item}?\n\n"
            f"\t(1) Yes\n\t(2) No\n\n"
        )
        check_values = _boolean_values
    elif item == "both":
        text = (
            f"Do you want to include a {name} file, directory, or neither?\n\n"
            f"\t(1) File\n\t(2) Directory\n\t(3) Neither\n\n"
        )
        check_values = _directory_or_file
    else:
        return None

    while True:
        clear_screen()
        value = input(text)
        with suppress(KeyError):
            return_value = check_values[value]
            if return_value is True:
                return_value = item
            return return_value


def _get_conditional_path(name, path):
    while True:
        clear_screen()
        value = input(
            f"Do you want to create a {name} file/path?\n\n"
            f"\t(1) Yes\n\t(2) No\n\n"
        )
        with suppress(KeyError):
            return _boolean_values[value]


# ==============================================================================
# >> CALL MAIN FUNCTION
# ==============================================================================
if __name__ == "__main__":

    _plugin_name = _get_plugin_name()

    # Was a valid plugin name given?
    _options = {
        "python": {},
        "file_or_directory": {},
        "paths": {},
    }
    for _key, _values in config["CONDITIONAL_PYTHON_FILES"].items():
        _key = f"{_key}.py"
        _options["python"][_key] = (
            _values.as_bool("always_create_file")
            or _get_extra_file(_key)
        )
        if not _options["python"][_key]:
            continue

        if (
            "always_create_translations_file" not in _values
            or "translations_file_path" not in _values
        ):
            continue

        _create_translations_file = _values.as_bool(
            "always_create_translations_file"
        )
        _translations_file_path = _values["translations_file_path"]
        _options["python"][f"{_key}_translations"] = _get_translation_file(
            _key,
            _create_translations_file,
        )
        _options["python"][f"{_key}_translation_path"] = _translations_file_path
    for _key, _values in config["CONDITIONAL_FILE_OR_DIRECTORY"].items():
        _options["file_or_directory"][_key] = _get_directory_or_file(
            name=_key,
            item=_values,
        )

    for _key, _value in config["CONDITIONAL_PATHS"].items():
        _options["paths"][_key] = _get_conditional_path(_key, _value)

    PluginCreater(
        plugin_name=_plugin_name,
        options=_options,
    ).create_plugin()
