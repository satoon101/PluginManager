import subprocess
import tkinter as tk


BUTTONS_PER_ROW = 4


class BaseInterface:

    name = None

    def __init__(self, window, main_run):
        self.window = window
        self.main_run = main_run

    def clear_grid(self):
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Exit":
                continue
            widget.destroy()

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

    def create_console_output(self, commands):

        process = subprocess.Popen(
            " && ".join(commands),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        self.window.rowconfigure(0, weight=8)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=1)
        self.window.columnconfigure(0, weight=1)
        output_text = tk.Text(self.window, wrap="word", font=("consolas", 10))
        output_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        output_text.insert(tk.END, stdout)
        if stderr:
            output_text.insert(tk.END, f"\nErrors:\n{stderr}")

    @staticmethod
    def on_click(option):
        raise NotImplementedError()
