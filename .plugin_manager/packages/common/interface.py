import subprocess
import sys
import tkinter as tk


BUTTONS_PER_ROW = 4


class TextRedirector:
    def __init__(self, text_widget, tag="stdout"):
        self.text_widget = text_widget
        self.tag = tag

    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message, (self.tag,))
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass  # Needed for compatibility with some streams


class BaseInterface:

    name = None
    stdout = None
    stderr = None

    def __init__(self, window, main_run):
        self.window = window
        self.main_run = main_run

    def clear_grid(self):
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Exit":
                continue
            widget.destroy()
        if self.stdout is None:
            return

        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.stdout = None
        self.stderr = None

    def create_grid(self, data):
        for i, label in enumerate(data):
            row = i // BUTTONS_PER_ROW
            col = i % BUTTONS_PER_ROW
            button = tk.Button(
                self.window,
                text=label,
                command=lambda l=label: self.on_click(l),
            )
            button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        for i in range(BUTTONS_PER_ROW):
            self.window.grid_columnconfigure(i, weight=1)

        for i in range((len(data) + BUTTONS_PER_ROW - 1) // BUTTONS_PER_ROW):
            self.window.grid_rowconfigure(i, weight=1)

    def add_back_button(self, command):
        back_button = tk.Button(
            self.window,
            text="Back",
            command=command,
        )
        back_button.place(x=10, y=730)

    def on_back_to_main(self):
        self.clear_grid()
        self.main_run()

    def get_console(self):
        self.window.rowconfigure(0, weight=8)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=1)
        self.window.columnconfigure(0, weight=1)
        console = tk.Text(self.window, wrap="word", font=("consolas", 10))
        console.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        console.tag_config("stdout", foreground="black")
        console.tag_config("stderr", foreground="red")
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = TextRedirector(console, "stdout")
        sys.stderr = TextRedirector(console, "stderr")
        return console

    @staticmethod
    def execute_console_commands(console, commands):
        process = subprocess.Popen(
            " && ".join(commands),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            console.insert("end", line)

    @staticmethod
    def on_click(option):
        raise NotImplementedError()
