import tkinter as tk
from game_logic import MemoryGameLogic

class MemoryGameGUI:
    def __init__(self):
        self.logic = MemoryGameLogic()
        self.window = tk.Tk()
        self.window.title("Memo Game")
        self.buttons = {}
        self.first_choice = None
        self._create_grid()

    def _create_grid(self):
        for i, key in enumerate(self.logic.blocks):
            btn = tk.Button(self.window, text="?", width=10, height=4,
                            command=lambda k=key: self.on_click(k))
            btn.grid(row=i//3, column=i%3)
            self.buttons[key] = btn

    def on_click(self, key):
        value = self.logic.get_value(key)
        self.buttons[key].config(text=str(value), state="disabled")

        if not self.first_choice:
            self.first_choice = key
        else:
            self.window.after(1000, self.check_match, self.first_choice, key)
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
            win_label.grid(row=3, column=0, columnspan=3)

    def run(self):
        self.window.mainloop()