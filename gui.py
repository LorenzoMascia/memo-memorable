import tkinter as tk
import tkinter.font as tkFont
from game_logic import MemoryGameLogic

class MemoryGameGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Memo Game")
        self.window.configure(bg="#f4f4f4")

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=14)
        self.window.option_add("*Font", default_font)

        self.logic = None
        self.buttons = {}
        self.first_choice = None
        self.size = None
        self._show_start_screen()

    def _show_start_screen(self):
        label = tk.Label(self.window, text="🧠 Select Grid Size", font=("Helvetica", 18, "bold"),
                        bg="#f4f4f4", fg="#333")
        label.pack(pady=20)

        button_frame = tk.Frame(self.window, bg="#f4f4f4")
        button_frame.pack(pady=10)

        for size in [2, 4, 6]:
            btn = tk.Button(button_frame, text=f"{size}x{size}", width=10,
                            height=2, bg="#007acc", fg="white", activebackground="#005f99",
                            font=("Helvetica", 14, "bold"),
                            command=lambda s=size: self._start_game(s))
            btn.pack(pady=8)

    def _start_game(self, size):
        self.size = size
        for widget in self.window.winfo_children():
            widget.destroy()

        self.logic = MemoryGameLogic(size)
        self.buttons = {}
        self.first_choice = None
        self._create_grid()
        self._add_reset_button()

    def _add_reset_button(self):
        reset_btn = tk.Button(self.window, text="🔁 Reset", font=("Helvetica", 14, "bold"),
                      bg="#d9534f", fg="white", activebackground="#c9302c",
                      command=self._reset_game)
        reset_btn.grid(row=self.size + 1, column=0, columnspan=self.size, sticky="ew", pady=10)

    def _reset_game(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        self.first_choice = None
        self.logic = None
        self._show_start_screen()


    def _create_grid(self):
        for i in range(self.size):
            self.window.grid_rowconfigure(i, weight=1)
            self.window.grid_columnconfigure(i, weight=1)

        for i, key in enumerate(self.logic.blocks):
            btn = tk.Button(self.window, text="?", font=("Helvetica", 20, "bold"),
                            bg="white", fg="#333", activebackground="#e6e6e6",
                            relief="raised", bd=2,
                            command=lambda k=key: self.on_click(k))
            row = i // self.size
            col = i % self.size
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self.buttons[key] = btn

    def on_click(self, key):
        value = self.logic.get_value(key)
        self.buttons[key].config(text=str(value), state="disabled")

        if not self.first_choice:
            self.first_choice = key
        else:
            self.window.after(800, self.check_match, self.first_choice, key)
            self.first_choice = None

    def check_match(self, key1, key2):
        if self.logic.check_match(key1, key2):
            self.buttons[key1].config(bg="green")
            self.buttons[key2].config(bg="green")
            self.logic.remove_blocks(key1, key2)
        else:
            self.buttons[key1].config(text="?", state="normal")
            self.buttons[key2].config(text="?", state="normal")

        if self.logic.has_won():
            for btn in self.buttons.values():
                btn.config(state="disabled")
            win_label = tk.Label(self.window, text="🎉 You won!", font=("Helvetica", 24, "bold"),
                     bg="#f4f4f4", fg="green")
            win_label.grid(row=self.size + 2, column=0, columnspan=self.size, pady=10)

    def run(self):
        self.window.mainloop()
