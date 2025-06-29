# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import configparser
import importlib
import sys
import subprocess
from contextlib import suppress
from pathlib import Path
import tkinter as tk


# =============================================================================
# >> CLASSES
# =============================================================================
class PluginManager(dict):

    window = None
    disabled_commands = list()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = Path(__file__).parent / ".plugin_manager"
        self.config_path = self.base_path.parent.joinpath("config.ini")

    def create_window(self):
        self.install_requirements()
        self.window = tk.Tk()
        self.window.title("Plugin Manager")
        self.window.geometry("1024x768")
        if not self.check_config():
            self.display_update_config_message()
            return

        self.window.grid_rowconfigure(0, weight=1)
        exit_button = tk.Button(
            self.window,
            text="Exit",
            command=self.window.quit,
        )
        exit_button.place(x=980, y=730)

    def populate_dictionary(self):
        package_path = self.base_path.joinpath("packages")
        sys.path.append(str(package_path))
        for file in package_path.glob("*.py"):
            if file.stem.startswith("_"):
                continue
            if file.stem in self.disabled_commands:
                continue
            module = importlib.import_module(file.stem)
            with suppress(AttributeError):
                self[file.stem] = module.Interface(self.window, self.run)

    def run(self):
        call_mainloop = False
        if self.window is None:
            call_mainloop = True
            self.create_window()

        self.window.title("Plugin Manager")
        if not self:
            self.populate_dictionary()

        for i, (key, value) in enumerate(self.items()):
            button = tk.Button(
                self.window,
                text=value.name,
                command=lambda l=key: self.on_click(l),
            )
            button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        for i in range(len(self)):
            self.window.grid_columnconfigure(i, weight=1)

        if call_mainloop:
            self.window.mainloop()

    def on_click(self, option):
        for widget in self.window.winfo_children():
            if widget.cget("text") == "Exit":
                continue
            widget.destroy()

        self[option].run()

    def install_requirements(self):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )
        pip_requirements = dict(
            line.split("==")
            for line in result.stdout.splitlines()
            if "==" in line
        )
        requirements_path = self.base_path.joinpath(
            "tools",
            "requirements.txt",
        )
        with open(requirements_path) as _open_file:
            requirements = dict(
                line.split("==")
                for line in _open_file.readlines()
                if "==" in line
            )
        for requirement, value in requirements.items():
            if requirement not in pip_requirements:
                break
            if value < pip_requirements[requirement]:
                break
        else:
            return
    
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path]
        )

    def check_config(self):
        if not self.config_path.is_file():
            config_path = self.base_path.joinpath("tools", "config.ini")
            with (
                config_path.open() as read_file,
                self.config_path.open('w') as write_file,
            ):
                write_file.write(read_file.read())
            return False

        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.disabled_commands = config["BASE SETTINGS"]["DISABLED_COMMANDS"]
        self.disabled_commands = self.disabled_commands.split(",")
        return True

    def display_update_config_message(self):
        label = tk.Label(
            self.window,
            text=f"Please update the configuration at {self.config_path}",
            font=("times", 24, "bold"),
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
        exit_button = tk.Button(self.window, text="Exit", command=self.window.quit)
        exit_button.place(x=980, y=730)
        self.window.mainloop()


instance = PluginManager()
instance.run()
