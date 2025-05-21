import tkinter as tk
from game_logic import MemoryGameLogic

class MemoryGameGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Memo Game")
        self.logic = None
        self.buttons = {}
        self.first_choice = None
        self.size = None
        self._show_start_screen()

    def _show_start_screen(self):
        label = tk.Label(self.window, text="Select Grid Size", font=("Arial", 16))
        label.pack(pady=10)

        for size in [3, 6, 9]:
            btn = tk.Button(self.window, text=f"{size}x{size}", width=10,
                            command=lambda s=size: self._start_game(s))
            btn.pack(pady=5)

    def _start_game(self, size):
        self.size = size
        for widget in self.window.winfo_children():
            widget.destroy()

        self.logic = MemoryGameLogic(size)
        self.buttons = {}
        self._create_grid()

    def _create_grid(self):
        for i in range(self.size):
            self.window.grid_rowconfigure(i, weight=1)
            self.window.grid_columnconfigure(i, weight=1)

        for i, key in enumerate(self.logic.blocks):
            btn = tk.Button(self.window, text="?", font=("Arial", 12),
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
            win_label = tk.Label(self.window, text="You won!", font=("Arial", 20))
            win_label.grid(row=self.size, column=0, columnspan=self.size)

    def run(self):
        self.window.mainloop()
