import tkinter as tk
import tkinter.font as tkFont
from app.game_logic import MemoryGameLogic
import time

# Predefined templates
TEMPLATES = {
    "Custom": [],
    "Numbers 4x4": [(str(i), str(i)) for i in range(1, 9)],
    "English Words A1": [
        ("hello", "ciao"),
        ("goodbye", "arrivederci"),
        ("thank you", "grazie"),
        ("yes", "sì"),
        ("no", "no"),
        ("book", "libro"),
        ("car", "macchina"),
        ("house", "casa")
    ],
    "Italian Food": [
        ("pizza", "pizza"),
        ("pasta", "pasta"),
        ("gelato", "ice cream"),
        ("espresso", "espresso"),
        ("mozzarella", "mozzarella"),
        ("bruschetta", "bruschetta"),
        ("lasagna", "lasagna"),
        ("carbonara", "carbonara")
    ]
}

class MemoryGameGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Memo Trainer")
        self.window.configure(bg="#f9f9f9")

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=12)
        self.window.option_add("*Font", default_font)

        self.logic = None
        self.buttons = {}
        self.first_choice = None
        self.timer_label = None
        self.start_time = None
        self.timer_running = False
        self.after_id = None
        self.waiting = False

        self.entries = []  # pairs entered by user
        self.selected_template = tk.StringVar(value="Custom")  # Template selected
        self._show_input_screen()

    def _show_input_screen(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        for widget in self.window.winfo_children():
            widget.destroy()

        title = tk.Label(self.window, text="🎓 Memorize Anything!", font=("Segoe UI", 16, "bold"),
                         bg="#f9f9f9", fg="#333")
        title.pack(pady=10)

        subtitle = tk.Label(self.window, text="Enter the pairs you want to memorize:\n(e.g., Term ↔ Definition)",
                            font=("Segoe UI", 12), bg="#f9f9f9", fg="#555", justify="center")
        subtitle.pack(pady=(0, 10))

        # Dropdown menu
        template_frame = tk.Frame(self.window, bg="#f9f9f9")
        template_frame.pack(pady=5)

        tk.Label(template_frame, text="Select Template:", font=("Segoe UI", 12), bg="#f9f9f9").pack(side=tk.LEFT)
        dropdown = tk.OptionMenu(template_frame, self.selected_template, *TEMPLATES.keys(), command=self._load_template)
        dropdown.config(width=20, font=("Segoe UI", 12))
        dropdown.pack(side=tk.LEFT, padx=5)

        example_frame = tk.Frame(self.window, bg="#f1f1f1", bd=1, relief="solid")
        example_frame.pack(pady=5, padx=10, ipadx=5, ipady=5)
        example_text = tk.Label(example_frame, text="Example:\nKey: Python\nValue: snake-like programming language",
                                font=("Segoe UI", 10, "italic"), bg="#f1f1f1", fg="#777")
        example_text.pack()

        self.form_frame = tk.Frame(self.window, bg="#f9f9f9")
        self.form_frame.pack()

        self.entries.clear()
        for _ in range(2):  # Start with 2 pairs
            self._add_pair_fields()

        add_btn = tk.Button(self.window, text="➕ Add Pair", command=self._add_pair_fields,
                            font=("Segoe UI", 12), bg="#007bff", fg="white")
        add_btn.pack(pady=10)

        start_btn = tk.Button(self.window, text="▶ Start Game", command=self._start_game,
                              font=("Segoe UI", 14), bg="#28a745", fg="white", padx=10, pady=5)
        start_btn.pack(pady=20)

        # Load current template
        self._load_template(self.selected_template.get())

    def _load_template(self, template_name):
        # Clear all entries
        for _, _, frame in self.entries:
            frame.destroy()
        self.entries.clear()

        # Load template data
        template_pairs = TEMPLATES[template_name]
        for key, value in template_pairs:
            self._add_pair_fields(key, value)

    def _add_pair_fields(self, key="", value=""):
        pair_frame = tk.Frame(self.form_frame, bg="#f9f9f9")
        pair_frame.pack(pady=5)

        term_entry = tk.Entry(pair_frame, width=30)
        def_entry = tk.Entry(pair_frame, width=30)
        term_entry.insert(0, key)
        def_entry.insert(0, value)

        remove_btn = tk.Button(
            pair_frame,
            text="❌",
            command=lambda: self._remove_pair(pair_frame, term_entry, def_entry),
            font=("Segoe UI", 10),
            fg="red",
            bg="#ffe6e6",
            relief="flat"
        )

        term_entry.pack(side=tk.LEFT, padx=5)
        def_entry.pack(side=tk.LEFT, padx=5)
        remove_btn.pack(side=tk.LEFT, padx=2)

        self.entries.append((term_entry, def_entry, pair_frame))

    def _remove_pair(self, frame, term_entry, def_entry):
        try:
            index_to_remove = None
            for i, (t, d, f) in enumerate(self.entries):
                if f == frame and t == term_entry and d == def_entry:
                    index_to_remove = i
                    break

            if index_to_remove is not None:
                self.entries.pop(index_to_remove)

            frame.destroy()
        except Exception as e:
            print("Error removing pair:", e)

    def _start_game(self):
        pairs = []
        for term_entry, def_entry, _ in self.entries:
            term = term_entry.get().strip()
            definition = def_entry.get().strip()
            if term and definition:
                pairs.append((term, definition))

        if len(pairs) < 2:
            tk.messagebox.showwarning("Error", "Please enter at least 2 valid pairs.")
            return

        self.logic = MemoryGameLogic(pairs)
        self.first_choice = None
        self.buttons = {}

        for widget in self.window.winfo_children():
            widget.destroy()

        self.timer_label = tk.Label(self.window, text="Time: 0s", bg="#f9f9f9", fg="#555", font=("Segoe UI", 12))
        self.timer_label.grid(row=0, column=0, columnspan=4, pady=5)

        self._create_grid()
        self._add_reset_button()

        self.start_time = time.time()
        self.timer_running = True
        self._start_timer()

    def _create_grid(self):
        keys = list(self.logic.blocks.keys())
        cols = 4
        for i, key in enumerate(keys):
            row, col = (i // cols) + 1, i % cols
            btn = tk.Button(self.window, text="?", font=("Segoe UI", 14, "bold"),
                            width=20, height=2, wraplength=180,
                            bg="white", relief="flat", bd=1, highlightbackground="#ccc",
                            command=lambda k=key: self._on_click(k))
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.buttons[key] = btn

    def _on_click(self, key):
        if not self.logic or key not in self.logic.blocks or self.waiting:
            return

        if self.first_choice == key:
            return

        value = self.logic.get_value(key)
        self.buttons[key].config(text=value, state="disabled", bg="#eef")

        if not self.first_choice:
            self.first_choice = key
        else:
            second_choice = key
            val1 = self.logic.get_value(self.first_choice)
            val2 = self.logic.get_value(second_choice)

            if self.logic.check_match(val1, val2):
                self.logic.remove_blocks(self.first_choice, second_choice)
                self.buttons[self.first_choice].config(bg="#28a745", fg="white")
                self.buttons[second_choice].config(bg="#28a745", fg="white")
                self.first_choice = None

                if self.logic.has_won():
                    self.timer_running = False
                    elapsed = int(time.time() - self.start_time)
                    win_label = tk.Label(self.window, text=f"🎉 You won in {elapsed} seconds!",
                                         font=("Segoe UI", 18, "bold"), bg="#f9f9f9", fg="#28a745")
                    win_label.grid(row=10, column=0, columnspan=4, pady=15)
            else:
                self.waiting = True
                first = self.first_choice
                self.first_choice = None

                def reset():
                    if first in self.buttons:
                        self.buttons[first].config(text="?", state="normal", bg="white")
                    if second_choice in self.buttons:
                        self.buttons[second_choice].config(text="?", state="normal", bg="white")
                    self.waiting = False

                self.window.after(1000, reset)

    def _start_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            try:
                self.timer_label.config(text=f"Time: {elapsed}s")
            except tk.TclError:
                return
            self.after_id = self.window.after(1000, self._start_timer)

    def _add_reset_button(self):
        reset_btn = tk.Button(self.window, text="🔁 New Game", font=("Segoe UI", 12, "bold"),
                              bg="#d9534f", fg="white", command=self._show_input_screen)
        reset_btn.grid(row=20, column=0, columnspan=4, sticky="ew", pady=10, padx=20)

    def run(self):
        self.window.mainloop()